import py
from rpython.flowspace.model import SpaceOperation, Constant, Variable
from rpython.rtyper.lltypesystem import lltype, llmemory, rffi
from rpython.translator.unsimplify import varoftype
from rpython.rlib import jit
from rpython.jit.codewriter.call import CallControl
from rpython.jit.codewriter import support

class FakePolicy:
    def look_inside_graph(self, graph):
        return True


def test_graphs_from_direct_call():
    cc = CallControl()
    F = lltype.FuncType([], lltype.Signed)
    f = lltype.functionptr(F, 'f', graph='fgraph')
    v = varoftype(lltype.Signed)
    op = SpaceOperation('direct_call', [Constant(f, lltype.Ptr(F))], v)
    #
    lst = cc.graphs_from(op, {}.__contains__)
    assert lst is None     # residual call
    #
    lst = cc.graphs_from(op, {'fgraph': True}.__contains__)
    assert lst == ['fgraph']     # normal call

def test_graphs_from_indirect_call():
    cc = CallControl()
    F = lltype.FuncType([], lltype.Signed)
    v = varoftype(lltype.Signed)
    graphlst = ['f1graph', 'f2graph']
    op = SpaceOperation('indirect_call', [varoftype(lltype.Ptr(F)),
                                          Constant(graphlst, lltype.Void)], v)
    #
    lst = cc.graphs_from(op, {'f1graph': True, 'f2graph': True}.__contains__)
    assert lst == ['f1graph', 'f2graph']     # normal indirect call
    #
    lst = cc.graphs_from(op, {'f1graph': True}.__contains__)
    assert lst == ['f1graph']     # indirect call, look only inside some graphs
    #
    lst = cc.graphs_from(op, {}.__contains__)
    assert lst is None            # indirect call, don't look inside any graph

def test_graphs_from_no_target():
    cc = CallControl()
    F = lltype.FuncType([], lltype.Signed)
    v = varoftype(lltype.Signed)
    op = SpaceOperation('indirect_call', [varoftype(lltype.Ptr(F)),
                                          Constant(None, lltype.Void)], v)
    lst = cc.graphs_from(op, {}.__contains__)
    assert lst is None

# ____________________________________________________________

class FakeJitDriverSD:
    def __init__(self, portal_graph):
        self.portal_graph = portal_graph
        self.portal_runner_ptr = "???"

def test_find_all_graphs():
    def g(x):
        return x + 2
    def f(x):
        return g(x) + 1
    rtyper = support.annotate(f, [7])
    jitdriver_sd = FakeJitDriverSD(rtyper.annotator.translator.graphs[0])
    cc = CallControl(jitdrivers_sd=[jitdriver_sd])
    res = cc.find_all_graphs(FakePolicy())
    funcs = set([graph.func for graph in res])
    assert funcs == set([f, g])

def test_find_all_graphs_without_g():
    def g(x):
        return x + 2
    def f(x):
        return g(x) + 1
    rtyper = support.annotate(f, [7])
    jitdriver_sd = FakeJitDriverSD(rtyper.annotator.translator.graphs[0])
    cc = CallControl(jitdrivers_sd=[jitdriver_sd])
    class CustomFakePolicy:
        def look_inside_graph(self, graph):
            assert graph.name == 'g'
            return False
    res = cc.find_all_graphs(CustomFakePolicy())
    funcs = [graph.func for graph in res]
    assert funcs == [f]

# ____________________________________________________________

def test_guess_call_kind_and_calls_from_graphs():
    class portal_runner_obj:
        graph = object()
    class FakeJitDriverSD:
        portal_runner_ptr = portal_runner_obj
    g = object()
    g1 = object()
    cc = CallControl(jitdrivers_sd=[FakeJitDriverSD()])
    cc.candidate_graphs = [g, g1]

    op = SpaceOperation('direct_call', [Constant(portal_runner_obj)],
                        Variable())
    assert cc.guess_call_kind(op) == 'recursive'

    op = SpaceOperation('direct_call', [Constant(object())],
                        Variable())
    assert cc.guess_call_kind(op) == 'residual'

    class funcptr:
        class graph:
            class func:
                oopspec = "spec"
    op = SpaceOperation('direct_call', [Constant(funcptr)],
                        Variable())
    assert cc.guess_call_kind(op) == 'builtin'

    class funcptr:
        graph = g
    op = SpaceOperation('direct_call', [Constant(funcptr)],
                        Variable())
    res = cc.graphs_from(op)
    assert res == [g]
    assert cc.guess_call_kind(op) == 'regular'

    class funcptr:
        graph = object()
    op = SpaceOperation('direct_call', [Constant(funcptr)],
                        Variable())
    res = cc.graphs_from(op)
    assert res is None
    assert cc.guess_call_kind(op) == 'residual'

    h = object()
    op = SpaceOperation('indirect_call', [Variable(),
                                          Constant([g, g1, h])],
                        Variable())
    res = cc.graphs_from(op)
    assert res == [g, g1]
    assert cc.guess_call_kind(op) == 'regular'

    op = SpaceOperation('indirect_call', [Variable(),
                                          Constant([h])],
                        Variable())
    res = cc.graphs_from(op)
    assert res is None
    assert cc.guess_call_kind(op) == 'residual'

# ____________________________________________________________

def test_get_jitcode():
    from rpython.jit.codewriter.test.test_flatten import FakeCPU
    class FakeRTyper:
        class annotator:
            translator = None
        class type_system:
            name = 'lltypesystem'
            @staticmethod
            def getcallable(graph):
                F = lltype.FuncType([], lltype.Signed)
                return lltype.functionptr(F, 'bar')
    #
    cc = CallControl(FakeCPU(FakeRTyper()))
    class somegraph:
        name = "foo"
    jitcode = cc.get_jitcode(somegraph)
    assert jitcode is cc.get_jitcode(somegraph)    # caching
    assert jitcode.name == "foo"
    pending = list(cc.enum_pending_graphs())
    assert pending == [(somegraph, jitcode)]

# ____________________________________________________________

def test_jit_force_virtualizable_effectinfo():
    py.test.skip("XXX add a test for CallControl.getcalldescr() -> EF_xxx")

def test_releases_gil_analyzer():
    from rpython.jit.backend.llgraph.runner import LLGraphCPU

    T = rffi.CArrayPtr(rffi.TIME_T)
    external = rffi.llexternal("time", [T], rffi.TIME_T, threadsafe=True)

    @jit.dont_look_inside
    def f():
        return external(lltype.nullptr(T.TO))

    rtyper = support.annotate(f, [])
    jitdriver_sd = FakeJitDriverSD(rtyper.annotator.translator.graphs[0])
    cc = CallControl(LLGraphCPU(rtyper), jitdrivers_sd=[jitdriver_sd])
    res = cc.find_all_graphs(FakePolicy())

    [f_graph] = [x for x in res if x.func is f]
    [block, _] = list(f_graph.iterblocks())
    [op] = block.operations
    call_descr = cc.getcalldescr(op)
    assert call_descr.extrainfo.has_random_effects()
    assert call_descr.extrainfo.is_call_release_gil() is False

def test_call_release_gil():
    from rpython.jit.backend.llgraph.runner import LLGraphCPU

    T = rffi.CArrayPtr(rffi.TIME_T)
    external = rffi.llexternal("time", [T], rffi.TIME_T, threadsafe=True)

    # no jit.dont_look_inside in this test
    def f():
        return external(lltype.nullptr(T.TO))

    rtyper = support.annotate(f, [])
    jitdriver_sd = FakeJitDriverSD(rtyper.annotator.translator.graphs[0])
    cc = CallControl(LLGraphCPU(rtyper), jitdrivers_sd=[jitdriver_sd])
    res = cc.find_all_graphs(FakePolicy())

    [llext_graph] = [x for x in res if x.func is external]
    [block, _] = list(llext_graph.iterblocks())
    [op] = block.operations
    call_target = op.args[0].value._obj.graph.func._call_aroundstate_target_
    call_target = llmemory.cast_ptr_to_adr(call_target)
    call_descr = cc.getcalldescr(op)
    assert call_descr.extrainfo.has_random_effects()
    assert call_descr.extrainfo.is_call_release_gil() is True
    assert call_descr.extrainfo.call_release_gil_target == call_target

def test_random_effects_on_stacklet_switch():
    from rpython.jit.backend.llgraph.runner import LLGraphCPU
    from rpython.translator.platform import CompilationError
    try:
        from rpython.rlib._rffi_stacklet import switch, handle
    except CompilationError as e:
        if "Unsupported platform!" in e.out:
            py.test.skip("Unsupported platform!")
        else:
            raise e
    @jit.dont_look_inside
    def f():
        switch(rffi.cast(handle, 0))

    rtyper = support.annotate(f, [])
    jitdriver_sd = FakeJitDriverSD(rtyper.annotator.translator.graphs[0])
    cc = CallControl(LLGraphCPU(rtyper), jitdrivers_sd=[jitdriver_sd])
    res = cc.find_all_graphs(FakePolicy())

    [f_graph] = [x for x in res if x.func is f]
    [block, _] = list(f_graph.iterblocks())
    op = block.operations[-1]
    call_descr = cc.getcalldescr(op)
    assert call_descr.extrainfo.has_random_effects()
