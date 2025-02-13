import py
from rpython.jit.backend.detect_cpu import getcpuclass
from rpython.jit.backend.test.runner_test import LLtypeBackendTest,\
     boxfloat, constfloat
from rpython.jit.metainterp.history import (BasicFailDescr, BasicFinalDescr,
                                            BoxInt)
from rpython.jit.metainterp.resoperation import ResOperation, rop
from rpython.jit.tool.oparser import parse
from rpython.rtyper.lltypesystem import lltype, llmemory, rclass
from rpython.rtyper.annlowlevel import llhelper
from rpython.jit.codewriter.effectinfo import EffectInfo
from rpython.jit.metainterp.history import JitCellToken, TargetToken


CPU = getcpuclass()

class FakeStats(object):
    pass


class TestARM(LLtypeBackendTest):

    # for the individual tests see
    # ====> ../../test/runner_test.py

    add_loop_instructions = ['ldr', 'mov', 'adds', 'cmp', 'beq', 'b']
    bridge_loop_instructions = ['ldr', 'mov', 'nop', 'cmp', 'bge',
                                'push', 'mov', 'mov', 'push', 'mov', 'mov',
                                'blx', 'mov', 'mov', 'bx']

    def get_cpu(self):
        cpu = CPU(rtyper=None, stats=FakeStats())
        cpu.setup_once()
        return cpu

    def test_result_is_spilled(self):
        cpu = self.cpu
        inp = [BoxInt(i) for i in range(1, 15)]
        out = [BoxInt(i) for i in range(1, 15)]
        looptoken = JitCellToken()
        targettoken = TargetToken()
        operations = [
            ResOperation(rop.LABEL, inp, None, descr=targettoken),
            ResOperation(rop.INT_ADD, [inp[0], inp[1]], out[0]),
            ResOperation(rop.INT_ADD, [inp[2], inp[3]], out[1]),
            ResOperation(rop.INT_ADD, [inp[4], inp[5]], out[2]),
            ResOperation(rop.INT_ADD, [inp[6], inp[7]], out[3]),
            ResOperation(rop.INT_ADD, [inp[8], inp[9]], out[4]),
            ResOperation(rop.INT_ADD, [inp[10], inp[11]], out[5]),
            ResOperation(rop.INT_ADD, [inp[12], inp[13]], out[6]),
            ResOperation(rop.INT_ADD, [inp[0], inp[1]], out[7]),
            ResOperation(rop.INT_ADD, [inp[2], inp[3]], out[8]),
            ResOperation(rop.INT_ADD, [inp[4], inp[5]], out[9]),
            ResOperation(rop.INT_ADD, [inp[6], inp[7]], out[10]),
            ResOperation(rop.INT_ADD, [inp[8], inp[9]], out[11]),
            ResOperation(rop.INT_ADD, [inp[10], inp[11]], out[12]),
            ResOperation(rop.INT_ADD, [inp[12], inp[13]], out[13]),
            ResOperation(rop.GUARD_FALSE, [inp[1]], None, descr=BasicFailDescr(1)),
            ResOperation(rop.FINISH, [inp[1]], None, descr=BasicFinalDescr(1)),
            ]
        operations[-2].setfailargs(out)
        cpu.compile_loop(inp, operations, looptoken)
        args = [i for i in range(1, 15)]
        deadframe = self.cpu.execute_token(looptoken, *args)
        output = [self.cpu.get_int_value(deadframe, i - 1) for i in range(1, 15)]
        expected = [3, 7, 11, 15, 19, 23, 27, 3, 7, 11, 15, 19, 23, 27]
        assert output == expected

    def test_redirect_call_assembler2(self):
        def assembler_helper(deadframe, virtualizable):
            x = self.cpu.get_int_value(deadframe, 0)
            assert x == 11
            return 7

        FUNCPTR = lltype.Ptr(lltype.FuncType([llmemory.GCREF, llmemory.GCREF],
                                             lltype.Signed))

        class FakeJitDriverSD:
            index_of_virtualizable = -1
            _assembler_helper_ptr = llhelper(FUNCPTR, assembler_helper)
            assembler_helper_adr = llmemory.cast_ptr_to_adr(
                _assembler_helper_ptr)
        FakeJitDriverSD.portal_calldescr = self.cpu.calldescrof(
            lltype.Ptr(lltype.FuncType([lltype.Signed], lltype.Signed)),
                [lltype.Signed], lltype.Signed, EffectInfo.MOST_GENERAL)
        lt1, lt2, lt3 = [JitCellToken() for x in range(3)]
        lt2.outermost_jitdriver_sd = FakeJitDriverSD()
        loop1 = parse('''
        [i0]
        i1 = call_assembler(i0, descr=lt2)
        guard_not_forced()[]
        finish(i1)
        ''', namespace=locals())
        loop2 = parse('''
        [i0]
        i1 = int_add(i0, 1)
        finish(i1)
        ''')
        loop3 = parse('''
        [i0]
        i1 = int_sub(i0, 1)
        finish(i1)
        ''')
        self.cpu.compile_loop(loop2.inputargs, loop2.operations, lt2)
        self.cpu.compile_loop(loop3.inputargs, loop3.operations, lt3)
        self.cpu.compile_loop(loop1.inputargs, loop1.operations, lt1)
        df = self.cpu.execute_token(lt1, 10)
        assert self.cpu.get_int_value(df, 0) == 7

        self.cpu.redirect_call_assembler(lt2, lt3)
        df = self.cpu.execute_token(lt1, 12)
        assert self.cpu.get_int_value(df, 0) == 7

    SFloat = lltype.GcForwardReference()
    SFloat.become(lltype.GcStruct('SFloat', ('parent', rclass.OBJECT),
          ('v1', lltype.Signed), ('v2', lltype.Signed),
          ('v3', lltype.Signed), ('v4', lltype.Signed),
          ('v5', lltype.Signed), ('v6', lltype.Signed),
          ('v7', lltype.Signed), ('v8', lltype.Signed),
          ('v9', lltype.Signed), ('v10', lltype.Signed),
          ('v11', lltype.Signed), ('v12', lltype.Signed),
          ('v13', lltype.Signed), ('v14', lltype.Signed),
          ('v15', lltype.Signed), ('v16', lltype.Signed),
          ('v17', lltype.Signed), ('v18', lltype.Signed),
          ('v19', lltype.Signed), ('v20', lltype.Signed),

          ('w1', lltype.Signed), ('w2', lltype.Signed),
          ('w3', lltype.Signed), ('w4', lltype.Signed),
          ('w5', lltype.Signed), ('w6', lltype.Signed),
          ('w7', lltype.Signed), ('w8', lltype.Signed),
          ('w9', lltype.Signed), ('w10', lltype.Signed),
          ('w11', lltype.Signed), ('w12', lltype.Signed),
          ('w13', lltype.Signed), ('w14', lltype.Signed),
          ('w15', lltype.Signed), ('w16', lltype.Signed),
          ('w17', lltype.Signed), ('w18', lltype.Signed),
          ('w19', lltype.Signed), ('w20', lltype.Signed),

          ('x1', lltype.Signed), ('x2', lltype.Signed),
          ('x3', lltype.Signed), ('x4', lltype.Signed),
          ('x5', lltype.Signed), ('x6', lltype.Signed),
          ('x7', lltype.Signed), ('x8', lltype.Signed),
          ('x9', lltype.Signed), ('x10', lltype.Signed),
          ('x11', lltype.Signed), ('x12', lltype.Signed),
          ('x13', lltype.Signed), ('x14', lltype.Signed),
          ('x15', lltype.Signed), ('x16', lltype.Signed),
          ('x17', lltype.Signed), ('x18', lltype.Signed),
          ('x19', lltype.Signed), ('x20', lltype.Signed),

          ('y1', lltype.Signed), ('y2', lltype.Signed),
          ('y3', lltype.Signed), ('y4', lltype.Signed),
          ('y5', lltype.Signed), ('y6', lltype.Signed),
          ('y7', lltype.Signed), ('y8', lltype.Signed),
          ('y9', lltype.Signed), ('y10', lltype.Signed),
          ('y11', lltype.Signed), ('y12', lltype.Signed),
          ('y13', lltype.Signed), ('y14', lltype.Signed),
          ('y15', lltype.Signed), ('y16', lltype.Signed),
          ('y17', lltype.Signed), ('y18', lltype.Signed),
          ('y19', lltype.Signed), ('y20', lltype.Signed),
          ('float', lltype.Float)))

    TFloat = lltype.GcStruct('TFloat', ('parent', SFloat),
                             ('next', lltype.Ptr(SFloat)))

    def test_float_field(self):
        if not self.cpu.supports_floats:
            py.test.skip('requires floats')
        floatdescr = self.cpu.fielddescrof(self.SFloat, 'float')
        t_box, T_box = self.alloc_instance(self.TFloat)
        self.execute_operation(rop.SETFIELD_GC, [t_box, boxfloat(3.4)],
                               'void', descr=floatdescr)
        res = self.execute_operation(rop.GETFIELD_GC, [t_box],
                                     'float', descr=floatdescr)
        assert res.getfloat() == 3.4
        #
        self.execute_operation(rop.SETFIELD_GC, [t_box, constfloat(-3.6)],
                               'void', descr=floatdescr)
        res = self.execute_operation(rop.GETFIELD_GC, [t_box],
                                     'float', descr=floatdescr)
        assert res.getfloat() == -3.6

    def test_compile_loop_many_int_args(self):
        for numargs in range(2, 30):
            ops = []
            arglist = "[%s]\n" % ", ".join(["i%d" % i for i in range(numargs)])
            ops.append(arglist)

            arg1 = 0
            arg2 = 1
            res = numargs
            for i in range(numargs - 1):
                op = "i%d = int_add(i%d, i%d)\n" % (res, arg1, arg2)
                arg1 = res
                res += 1
                arg2 += 1
                ops.append(op)
            ops.append("finish(i%d)" % (res - 1))

            ops = "".join(ops)
            loop = parse(ops)
            looptoken = JitCellToken()
            self.cpu.compile_loop(loop.inputargs, loop.operations, looptoken)
            ARGS = [lltype.Signed] * numargs
            RES = lltype.Signed
            args = [i+1 for i in range(numargs)]
            deadframe = self.cpu.execute_token(looptoken, *args)
            assert self.cpu.get_int_value(deadframe, 0) == sum(args)

    def test_debugger_on(self):
        py.test.skip("I don't care for now")
        from rpython.rlib import debug

        targettoken, preambletoken = TargetToken(), TargetToken()
        loop = """
        [i0]
        label(i0, descr=preambletoken)
        debug_merge_point('xyz', 0)
        i1 = int_add(i0, 1)
        i2 = int_ge(i1, 10)
        guard_false(i2) []
        label(i1, descr=targettoken)
        debug_merge_point('xyz', 0)
        i11 = int_add(i1, 1)
        i12 = int_ge(i11, 10)
        guard_false(i12) []
        jump(i11, descr=targettoken)
        """
        ops = parse(loop, namespace={'targettoken': targettoken,
                                     'preambletoken': preambletoken})
        debug._log = dlog = debug.DebugLog()
        try:
            self.cpu.assembler.set_debug(True)
            looptoken = JitCellToken()
            self.cpu.compile_loop(ops.inputargs, ops.operations, looptoken)
            self.cpu.execute_token(looptoken, 0)
            # check debugging info
            struct = self.cpu.assembler.loop_run_counters[0]
            assert struct.i == 1
            struct = self.cpu.assembler.loop_run_counters[1]
            assert struct.i == 1
            struct = self.cpu.assembler.loop_run_counters[2]
            assert struct.i == 9
            self.cpu.finish_once()
        finally:
            debug._log = None
        l0 = ('debug_print', 'entry -1:1')
        l1 = ('debug_print', preambletoken.repr_of_descr() + ':1')
        l2 = ('debug_print', targettoken.repr_of_descr() + ':9')
        assert ('jit-backend-counts', [l0, l1, l2]) in dlog
