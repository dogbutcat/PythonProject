
from typing import *
from collections import defaultdict
import struct
import enum

from binaryninja.basicblock import BasicBlock
from binaryninja.function import Function
from binaryninja.variable import (
    Variable, RegisterValue,
    ConstantRegisterValue,
)
from binaryninja.enums import (
    BranchType,
    MediumLevelILOperation,
    HighLevelILOperation,
)
from binaryninja.mediumlevelil import (
    MediumLevelILBasicBlock,
    MediumLevelILFunction,
    MediumLevelILCallSsa,
    MediumLevelILIf,
    MediumLevelILVarPhi,
    MediumLevelILMemPhi,
    MediumLevelILVarSsa,
    MediumLevelILSetVarSsa,
    MediumLevelILSetVarSsaField,
    MediumLevelILVarSsaField,
    MediumLevelILCmpNe,
    MediumLevelILCmpE,
    MediumLevelILCmpSgt,
    MediumLevelILCmpSle,
    SSAVariable,
    MediumLevelILVar,
    MediumLevelILConst,
    MediumLevelILSetVar,
    MediumLevelILZx,
    MediumLevelILRet,
)

from binaryninja.architecture import Architecture


class JumpEnums(enum.IntEnum):
    TrueOut = 2
    FalseOut = 3
    DirectOut = 1

# def get_all_phi_node(func: Function):
#     phi_node: List['MediumLevelILVarPhi'] = []
#     for inss in func.medium_level_il.ssa_form.instructions:
#         if inss.operation == MediumLevelILOperation.MLIL_VAR_PHI:
#             phi_node.append(inss)

#     return phi_node

def get_cff_nodes(func: Function) -> List['MediumLevelILBasicBlock']:
    cff_nodes = []
    for block in func.mlil.basic_blocks:
        # dominated_counts = sum([(1 if block in x.source.dominators else 0) for x in block.incoming_edges])
        dominated_counts = 0
        for edge in block.incoming_edges:
            if block in edge.source.dominators:
                dominated_counts = dominated_counts + 1
        if dominated_counts >= 3:
            cff_nodes.append(block)
    return cff_nodes

def replace_phi_def_var(cff_node:MediumLevelILBasicBlock) -> List[Tuple['MediumLevelILBasicBlock','MediumLevelILSetVarSsa']]:
    mlil_func = cff_node.il_function.ssa_form
    instructions = list(mlil_func.instructions)
    assign_ins:List['MediumLevelILSetVarSsa'] = []
    for ins in instructions[cff_node.start:cff_node.end]:
        if isinstance(ins, MediumLevelILSetVarSsa) and isinstance(ins.src, MediumLevelILVarSsa):
            assign_ins.append(ins)
    warn_list = []
    for ins in assign_ins:
        dest_ssa_var = ins.dest
        all_var_uses = mlil_func.get_ssa_var_uses(dest_ssa_var)
        all_var_uses = list(filter(lambda x: not isinstance(x, MediumLevelILVarPhi),all_var_uses))
        for use_ins in all_var_uses:
            # print(use_ins)
            last_ins_block = mlil_func[use_ins.il_basic_block.end -1]
            if (isinstance(last_ins_block, MediumLevelILRet)):
                warn_list.append((use_ins.il_basic_block, ins))
                break
            # print(use_ins.il_basic_block.source_block.disassembly_text)
    return warn_list
    # print(assign_ins)

def get_dom_child_blocks(cff_node: MediumLevelILBasicBlock) -> List['MediumLevelILBasicBlock']:
    blocks = set()
    to_visit:List['MediumLevelILBasicBlock'] = [cff_node]
    while len(to_visit):
        block = to_visit.pop()
        for in_edge in block.incoming_edges:
            parent_block = in_edge.source
            # print(parent_block,sorted(parent_block.dominators,reverse=True))
            if cff_node in parent_block.dominators and parent_block not in blocks:
                blocks.add(parent_block)
                to_visit.append(parent_block)

    # last_mlil_ssa_ins = cff_node.il_function.ssa_form[cff_node.end - 1]
    # is_cond = False
    # if isinstance(last_mlil_ssa_ins, MediumLevelILIf):
    #     cond_var = last_mlil_ssa_ins.condition.vars_read[0]
    #     if cond_var.name.startswith('cond'):
    #         is_cond = True
    for in_edge in cff_node.incoming_edges:
        parent_block = in_edge.source
        # print(parent_block,sorted(parent_block.dominators,reverse=True))
        if parent_block not in blocks:
            blocks.add(parent_block)
            # ins_count = get_condition_block_instruction_count(cff_node)
            # if (is_cond and ins_count == 2):
            #     blocks.add(parent_block)
            # elif (ins_count == 1):
            #     blocks.add(parent_block)
    return sorted(blocks)

def is_state_var(phi_ins: 'MediumLevelILVarPhi', target_var: SSAVariable | Variable | MediumLevelILVarSsaField, depth: int = 0) -> bool:
    mlil_ssa = phi_ins.il_basic_block.il_function.ssa_form
    if isinstance(target_var, MediumLevelILVarSsaField):
        target_var = target_var.src
    def_var_ins = mlil_ssa.get_ssa_var_definition(target_var)
    # print(def_var_ins,type(def_var_ins), type(def_var_ins.src))
    ret_val = False
    if depth > 100:
        # too much recursive
        # print('comes to an end in False')
        # print(phi_ins.dest, target_var, depth)
        return ret_val
    # check var has re-assign to var which in phi node
    # print(mlil_ssa.get_ssa_var_uses(target_var))
    # print(phi_ins.dest, target_var, depth)
    if isinstance(def_var_ins, MediumLevelILSetVarSsa):
        if isinstance(def_var_ins.src, MediumLevelILVarSsa):
            # print(def_var_ins)
            ret_val = is_state_var(phi_ins, def_var_ins.src.var, depth + 1)
        elif isinstance(def_var_ins.src, MediumLevelILZx):
            zx_var = def_var_ins.src
            ret_val = is_state_var(phi_ins, zx_var.vars_read[0], depth + 1)
        elif isinstance(def_var_ins.src, MediumLevelILConst):
            # var = const
            # get all use
            def_var_uses = mlil_ssa.get_ssa_var_uses(def_var_ins.dest)
            # print((def_var_ins))
            # print((def_var_uses))
            for def_var_use in def_var_uses:
                ret_val= is_state_var(phi_ins, def_var_use.dest, depth + 1)
                # print('%s returns %d' % (def_var_use.dest, ret))
                if ret_val:
                    return ret_val
            ret_val = False

    elif isinstance(def_var_ins, MediumLevelILVarPhi):
        # print('need identify phi ins: %s' % def_var_ins.dest)
        if def_var_ins.dest in phi_ins.vars_read + phi_ins.vars_written:
            ret_val = True
        else:
            # print('do phi ins: ', def_var_ins)
            ret_val = is_state_var(phi_ins, def_var_ins.dest, depth + 1)
        # print(ret_val)
    elif isinstance(def_var_ins, MediumLevelILCallSsa):
        ret_val = False
    else:
        # print(def_var_ins)
        # print(type(def_var_ins.src))
        print('unknown ins: %s from %s' % (def_var_ins, target_var))
        ret_val = False
    return ret_val

def get_conds_in_blocks( phi_ins: 'MediumLevelILVarPhi', blocks: List['MediumLevelILBasicBlock']) -> List['MediumLevelILIf']:
    blocks_to_visit = list(blocks)
    conditions = set()
    while len(blocks_to_visit):
        block = blocks_to_visit.pop()
        for in_edge in block.incoming_edges:
            parent_block: MediumLevelILBasicBlock = in_edge.source
            # print(type(parent_block))
            last_mlil_ins = parent_block.il_function[parent_block.end - 1]
            if isinstance(last_mlil_ins, MediumLevelILIf):
                cond_var = last_mlil_ins.condition.vars_read[0]
                if cond_var.name.startswith('cond'):
                    temp, _, _ = get_original_cond_ins(last_mlil_ins.condition.il_basic_block.il_function,cond_var)
                    # print(temp)
                    # print(cond_var)
                    if isinstance(temp, MediumLevelILVarSsaField):
                        cond_var = temp.src
                    elif isinstance(temp, MediumLevelILVarSsa):
                        cond_var = temp.var
                    else:
                        print('Unknown %s in type %s' %(temp, type(temp)))
                ret = is_state_var(phi_ins, cond_var)
                # print(cond_var)
                # print(ret)
                if ret:
                    conditions.add(last_mlil_ins)
    # print(list(conditions))
    return list(conditions)

def get_original_cond_ins(func: MediumLevelILFunction, variable: Variable | SSAVariable) -> Tuple[Variable | SSAVariable, Variable | SSAVariable, int]:
    var_def = (func.get_ssa_var_definition(variable))
    # print(var_def.src)
    return var_def.src.left, var_def.src.right, var_def.src.operation

def get_state_var(conditions: List['MediumLevelILIf']) -> SSAVariable | Variable:
    var_counts: Dict['SSAVariable | Variable', int] = defaultdict(lambda: 0)
    for condition in conditions:
        # print((condition.condition.vars_read[0]))
        # print(dir(condition.condition))
        for var in condition.condition.vars_read:
            if var.name.startswith('cond'):
                var, _, _ = get_original_cond_ins(condition.il_basic_block.il_function,var)
            var_counts[var] += 1
    target_var = max(var_counts.items(), key=lambda x: x[1])[0]
    return target_var

def get_condition_block_instruction_count(condition_block: MediumLevelILBasicBlock):
    # print(list(filter(lambda x: not isinstance(x, (MediumLevelILVarPhi, MediumLevelILMemPhi)), map(lambda x: x.il_instruction, condition_block.get_disassembly_text()))))
    return len(list(filter(lambda x: not isinstance(x, (MediumLevelILVarPhi, MediumLevelILMemPhi)), map(lambda x: x.il_instruction, condition_block.get_disassembly_text()))))

def get_const_map(conditions: List['MediumLevelILIf'], state_var_defs:Dict['MediumLevelILBasicBlock','ConstantRegisterValue']) -> Dict['ConstantRegisterValue', Tuple['MediumLevelILBasicBlock', int, Literal[JumpEnums.TrueOut, JumpEnums.FalseOut, JumpEnums.DirectOut], 'MediumLevelILBasicBlock']]:
    const_dict = {}
    for condition in conditions:
        if not isinstance(condition.condition, (MediumLevelILCmpE, MediumLevelILCmpNe, MediumLevelILVar, MediumLevelILVarSsa)):
            continue

        cond_var = condition.condition
        # print(condition.il_basic_block)
        # print(len(list(filter(lambda x: not isinstance(x, (MediumLevelILVarPhi, MediumLevelILMemPhi)), map(lambda x: x.il_instruction, condition.il_basic_block.get_disassembly_text())))))
        # print( condition.il_basic_block if (condition.il_basic_block in state_var_defs) else False)
        # print(type(condition))
        is_cond = False
        if isinstance(cond_var, ( MediumLevelILVar, MediumLevelILVarSsa)):
            left, right, operation = get_original_cond_ins(condition.il_basic_block.il_function, cond_var)
            is_cond = True

        else:
            left = cond_var.left
            right = cond_var.right
            operation = cond_var.operation
        # print(type(left), type(right))
        if isinstance(left,(MediumLevelILVar, MediumLevelILVarSsa, MediumLevelILVarSsaField)):
            const_var = right
            compared_var = left
        elif isinstance(left, MediumLevelILConst):
            const_var = left
            compared_var = right
        else:
            print('skipping current condition: %s' % condition)
            continue

        if (operation == MediumLevelILOperation.MLIL_CMP_E):
            judge = JumpEnums.TrueOut
            target_block_idx = condition.true
        elif operation == MediumLevelILOperation.MLIL_CMP_NE:
            judge = JumpEnums.FalseOut
            target_block_idx = condition.false

        # this means jump ins to is not single instruction, need to keep
        # most time will replace current const to further jump
        ins_count= get_condition_block_instruction_count(condition.il_basic_block)
        mlil_ssa_func = condition.function.ssa_form
        target_block = mlil_ssa_func.get_basic_block_at(target_block_idx)
        if cond_var in state_var_defs:
            judge = JumpEnums.DirectOut
            const_dict[const_var.value] = (condition.il_basic_block, const_var.value, judge, target_block)
            continue
        # if is_cond and ins_count > 2:
        #     judge = JumpEnums.DirectOut
        #     const_dict[const_var.value] = (condition.il_basic_block, const_var.value, judge, target_block)
        #     # continue
        # elif ins_count > 1:
        #     judge = JumpEnums.DirectOut
        #     const_dict[const_var.value] = (condition.il_basic_block, const_var.value, judge, target_block)
        #     # continue
        # else:
            # print((condition.function.get_basic_block_at(target_block)))
        const_dict[const_var.value] = (target_block, const_var.value, judge, target_block)
    # print('const dict: %s' % const_dict)
    # print('%s' % conditions)
    return const_dict

def get_state_var_defs(state_var: SSAVariable | Variable, blocks:List['MediumLevelILBasicBlock']) -> Dict['MediumLevelILBasicBlock', 'ConstantRegisterValue']:
    state_var_defs = {}
    # print(type(list(blocks[0].il_function.instructions)[67]))
    for block in blocks:
        instructions = list(block.il_function.instructions)[block.start:block.end]
        # print(instructions)
        # print()
        for ins in instructions:
            # print((state_var.var))
            # print(ins.dest if isinstance(ins, MediumLevelILSetVarSsa) else '')
            if isinstance(ins, (MediumLevelILSetVar, MediumLevelILSetVarSsa)) and ins.dest == state_var:
                # print(dir(ins))
                # print(type(ins.src.value))
                # print(state_var)
                state_var_defs[block] = ins.src.value
    # find where state var init
    for ins in list(block.il_function.instructions):
        if isinstance(ins, (MediumLevelILSetVar, MediumLevelILSetVarSsa)) and isinstance(ins.src, (MediumLevelILConst, )) and ins.dest == state_var:
            # print(ins.operands)
            # print(ins.il_basic_block)
            state_var_defs[ins.il_basic_block] = ins.src.value
    return state_var_defs

def generate_cfg(const_dict: Dict['ConstantRegisterValue', Tuple['MediumLevelILBasicBlock', int, Literal[JumpEnums.TrueOut, JumpEnums.FalseOut, JumpEnums.DirectOut], 'MediumLevelILBasicBlock']], state_var_defs: Dict['MediumLevelILBasicBlock', 'ConstantRegisterValue']) -> List[Tuple['MediumLevelILBasicBlock','MediumLevelILBasicBlock']]:
    # map state_var_defs to const_dict
    # print(const_dict)
    # print(state_var_defs)
    cfg_links:List[Tuple['MediumLevelILBasicBlock','MediumLevelILBasicBlock']] = []
    for def_block, const in state_var_defs.items():
        if const in const_dict:
            # if const_dict[const] in state_var_defs:
            #     print('found duplicate block in %s' % (const_dict[const]))
            #     recursive_block =  get_recursive_target(const_dict[const], const_dict, state_var_defs)
            #     print('found recursive block %s' % recursive_block)
            #     link = (def_block, recursive_block)
            # else:
            link = (def_block, const_dict[const])
            print('identity 0x%x jump from block %s at 0x%x to %s at 0x%x judge is %d' % (const.value, (link[0]), link[0].source_block.start, link[1][0], link[1][0].source_block.start, link[1][1]))
            cfg_links.append(link)
        else:
            # print(const)
            # print(const_dict)
            print('state block %s at 0x%x not found in const dict' % (def_block, def_block.source_block.start))

    # filter duplicate source block
    source_blocks: Dict['BasicBlock', List[Tuple['MediumLevelILBasicBlock', int]]] = {}
    while len(cfg_links):
        def_block, target_block = cfg_links.pop()
        if def_block.source_block not in source_blocks:
            source_blocks[def_block.source_block] = [target_block]
        else:
            source_blocks[def_block.source_block].append(target_block)
    
    print( '\n'.join( '%s: %s' % (hex(b.start), v) for b, v in source_blocks.items()))

    # reconstruct cfg
    new_cfg_links:List[Tuple['MediumLevelILBasicBlock','MediumLevelILBasicBlock']|Tuple['MediumLevelILBasicBlock','MediumLevelILBasicBlock','MediumLevelILBasicBlock']] = []
    for def_block, sub_arr in source_blocks.items():
        if len(sub_arr) == 1:
            jump_block, _, judge, target_block = sub_arr[0]
            if judge is JumpEnums.DirectOut:
                new_cfg_links.append((jump_block.source_block, target_block))
            link = (def_block, jump_block)
        elif len(sub_arr) == 2:
            # get cond
            # get true/false edge const
            # match const in array
            # set block, true, false
            # print(def_block.index)
            # print(def_block.function.mlil.ssa_form.basic_blocks[def_block.index])\
            # print(sub_arr)
            true_block, false_block = get_medium_il_branch_block(def_block)
            item1, item2 = sub_arr
            jump_block1, const_var1, judge1, target_block1 = item1
            jump_block2, _, judge2, target_block2 = item2

            # continue the judge
            if judge1 is JumpEnums.DirectOut:
                new_cfg_links.append((jump_block1.source_block, target_block1))
            if judge2 is JumpEnums.DirectOut:
                new_cfg_links.append((jump_block2.source_block, target_block2))

            ret = check_const_in_block(const_var1, true_block)
            if ret:
                true_block = jump_block1
                false_block = jump_block2
            else:
                true_block = jump_block2
                false_block = jump_block1
            link = (def_block, true_block, false_block)
            # print("%s %s %s" % (hex(def_block.start), true_block, false_block))
        else:
            print('todo')
        new_cfg_links.append(link)

    print('\n'.join('%s: %s' % (hex(bs[0].start),bs[1:]) for bs in new_cfg_links))
    # print(len(new_cfg_links))
    return new_cfg_links

def get_medium_il_branch_block(basic_block: BasicBlock) -> Tuple['MediumLevelILBasicBlock', 'MediumLevelILBasicBlock'] | None:
    func = basic_block.function
    found_block = None
    for block in func.mlil.ssa_form.basic_blocks:
        if block.source_block.start == basic_block.start:
            # print(basic_block.source_block)
            # print(block.source_block)
            found_block = block
            break
    print(found_block.start)
    if found_block is not None:
        out_edge1, out_edge2 = found_block.outgoing_edges
        if out_edge1.type == BranchType.TrueBranch:
            return out_edge1.target,out_edge2.target
        else:
            return out_edge2.target, out_edge1.target

def check_const_in_block(const_var: MediumLevelILConst, block: MediumLevelILBasicBlock) -> bool:
    for ins in list(block.il_function.instructions)[block.start: block.end]:
        if isinstance(ins, MediumLevelILSetVarSsa):
            ins_const_var = ins.src
            # print(ins)
            # print(const_var)
            # print(ins_const_var.value == const_var.value)
            if ins_const_var.value.value == const_var.value:
                return True
    return False

# def get_recursive_target(target: MediumLevelILBasicBlock, const_dict: Dict['ConstantRegisterValue', 'MediumLevelILBasicBlock'], state_var_defs: Dict['MediumLevelILBasicBlock', 'ConstantRegisterValue']) -> Tuple['MediumLevelILBasicBlock','MediumLevelILBasicBlock']:
#     const = state_var_defs.get(target)
#     if const in const_dict:
#         next_const_block = const_dict[const]
#         if next_const_block in state_var_defs:
#             return get_recursive_target(next_const_block, const_dict, state_var_defs)
#         else:
#             return next_const_block
#     else:
#         return target

def assemble_code(str: str, addr: int) -> bytes:
    print(str, hex(addr))
    return Architecture[func.arch.name].assemble(str, addr)

def generate_patch(cfg_links: List[Tuple['BasicBlock','MediumLevelILBasicBlock']|Tuple['BasicBlock','MediumLevelILBasicBlock','MediumLevelILBasicBlock']], func: Function) -> List[Tuple['int', 'bytes']]:
    # print(cfg_links)
    patch_data = []
    patch_objs = []
    cmp_tuple = ('eq', 'ne', 'cc', 'cs', 'mi', 'gt')
    pack_out = 'L'
    pack_in = 'l'
    if func.arch.name in ('aarch64'):
        pack_out = 'Q'
        pack_in = 'q'

    for link in cfg_links:
        if len(link) == 2:
            # continue
            from_block, out_block = link
            # func = from_block.function
            # asm_basic_block = func.get_basic_block_at(func.mlil[from_block.start].address)
            asm_basic_block = from_block
            last_ins = asm_basic_block.disassembly_text[-1]
            last_ins_address = last_ins.address
            ins_len = asm_basic_block.end - last_ins_address

            # if 'break' in list(map(lambda x: x.text,out_block.disassembly_text[0].tokens)):
            #     out_block = out_block.outgoing_edges[0].target
            # out_asm_basic_block = func.get_basic_block_at(func.mlil[out_block.start].address)
            out_asm_basic_block = out_block.source_block
            if out_block.get_disassembly_text()[0].tokens[0].text.startswith('goto'):
                out_asm_basic_block = out_asm_basic_block.outgoing_edges[0].target
                print('this block is only goto %s , advance to %s' % (out_block, out_block.outgoing_edges[0].target))
            out_address = out_asm_basic_block.start
            print('Patch at 0x%x, to 0x%x, %d bytes' % (last_ins_address, out_address, ins_len))
            original_bytecode = bv.read(last_ins_address, ins_len)
            jmp_unsigned_offset = struct.unpack(pack_out, struct.pack(pack_in, out_address - last_ins_address))[0]
            if jmp_unsigned_offset == 0x4:
            # if False:
                new_bytecode = assemble_code('nop', last_ins_address)
                print('Replacing %s with %s in nop' % (original_bytecode.hex(), new_bytecode.hex()))
            else:
                new_bytecode = assemble_code('b %s' % (jmp_unsigned_offset), last_ins_address)
                print('Replacing %s with %s offset %s' % (original_bytecode.hex(), new_bytecode.hex(), out_address - last_ins_address))
            patch = (last_ins_address, new_bytecode)
            patch_obj = {"b %s":(last_ins_address, out_address)}

            patch_data.append(patch)
            patch_objs.append(patch_obj)

        elif len(link) == 3:
            # continue
            base_block, true_block, false_block = link
            asm_basic_block = base_block
            true_block_source = true_block.source_block
            false_block_source = false_block.source_block

            true_block_address = true_block_source.start
            false_block_address = false_block_source.start

            if true_block_source.get_disassembly_text()[0].tokens[0].text.startswith('goto'):
                true_block_source = true_block_source.outgoing_edges[0].target
                print('true block is only goto %s , advance to %s' % (true_block_source, true_block_source.outgoing_edges[0].target))
            if false_block_source.get_disassembly_text()[0].tokens[0].text.startswith('goto'):
                false_block_source = false_block_source.outgoing_edges[0].target
                print('true block is only goto %s , advance to %s' % (false_block_source, false_block_source.outgoing_edges[0].target))

            last_ins = asm_basic_block.disassembly_text[-1]
            if last_ins.tokens[0].text.startswith('b') and func.arch.name == 'aarch64':
                csel_ins = asm_basic_block.disassembly_text[-2]
                if csel_ins.tokens[0].text.startswith('csel'):
                    filtered_token = list(filter(lambda x: x.text in cmp_tuple, csel_ins.tokens))[0]
                    # do address offset
                    csel_ins_address = csel_ins.address
                    last_ins_address = last_ins.address

                    ins_len = asm_basic_block.end - last_ins_address
                    csel_ins_len = last_ins_address - csel_ins_address

                    print('Patch True at 0x%x, to 0x%x, %d bytes' % (csel_ins_address, true_block_address, csel_ins_len))
                    print('Patch False at 0x%x, to 0x%x, %d bytes' % (last_ins_address, false_block_address, ins_len))

                    # original_csel_bytecode = bv.read(csel_ins_address, csel_ins_len)
                    # original_jump_bytecode = bv.read(last_ins_address, ins_len)
                    original_bytecode = bv.read(csel_ins_address, csel_ins_len+ins_len)

                    csel_jump_unsigned_offset = struct.unpack(pack_out, struct.pack(pack_in, true_block_address - csel_ins_address))[0]
                    false_jump_unsigned_offset = struct.unpack(pack_out, struct.pack(pack_in, false_block_address - last_ins_address))[0]
                    # new_csel_bytecode = Architecture[bv.arch.name].assemble('b.%s %s' % (filtered_token, hex(csel_jump_unsigned_offset)), csel_ins_address)
                    # new_direct_jump_bytecode = Architecture[bv.arch.name].assemble('b %s' % (hex(direct_jump_unsigned_offset)),last_ins_address)
                    patch_bytecode = assemble_code('b.%s %s\nb %s'%(filtered_token, hex(csel_jump_unsigned_offset), hex(false_jump_unsigned_offset)),csel_ins_address)
                    print('Replacing %s with %s at %s' % (original_bytecode.hex(), patch_bytecode.hex(), hex(csel_ins_address)))
                    # print('Replacing csel %s with %s offset %s' % (original_csel_bytecode.hex(), new_csel_bytecode.hex(), hex(csel_jump_unsigned_offset)))
                    # print('Replacing direct jump %s with %s offset %s' % (original_jump_bytecode.hex(), new_direct_jump_bytecode.hex(), hex(direct_jump_unsigned_offset)))
                    # patch = [(csel_ins_address, new_csel_bytecode), (last_ins_address, new_direct_jump_bytecode)]
                    patch = (csel_ins_address, patch_bytecode)
                    patch_obj = {f"b.{filtered_token} %s\nb %s":(csel_ins_address, true_block_address, false_block_address)}
                    patch_data.append(patch)
                    patch_objs.append(patch_obj)
            elif func.arch.name == 'thumb2':
                # inss = list(asm_basic_block.function.instructions)
                # filtered_inss = list(filter(lambda x: x[1]>=asm_basic_block.start and x[1]<asm_basic_block.end,inss))
                filtered_inss = asm_basic_block.disassembly_text
                it_ins = None
                it_idx = -1
                affect_line = 0
                jump_token = None
                it_dict = {"eq":"ne","ne":"eq","gt":"le","mi":"pl","hi":"ls"}
                # find itt/itttt
                for idx, ins in enumerate(filtered_inss):
                    it_token_text = ins.tokens[0].text
                    if it_token_text.startswith('it'):
                        it_ins = ins
                        it_idx = idx
                        affect_line = 1
                        # print(ins.tokens)
                        jump_token = list(filter(lambda x: x.text in cmp_tuple, ins.tokens))[0]
                        if it_token_text.startswith('itt'):
                            affect_line = 2
                            if it_token_text.startswith('itttt'):
                                affect_line = 4
                            break
                if it_ins is not None:
                    it_ins_addr = it_ins.address

                    is_end_condition = it_idx + affect_line + 1 == len(filtered_inss) - 1
                    if is_end_condition:
                        # get it section byte length
                        it_else_ins = filtered_inss[it_idx + affect_line + 1]
                        it_block_len = it_else_ins.address - it_ins_addr

                        # it_ins_addr includes it ins
                        true_jump_unsigned_offset = struct.unpack(pack_out, struct.pack(pack_in, true_block_address - it_ins_addr))[0]
                        true_it_size = len(assemble_code('b%s %s'%(jump_token, hex(true_jump_unsigned_offset)),it_ins_addr))
                        print(hex(true_block_address))
                        print(hex(it_ins_addr))
                        false_jump_start_addr = it_ins_addr + true_it_size
                        false_jump_unsigned_offset = struct.unpack(pack_out, struct.pack(pack_in, false_block_address - false_jump_start_addr))[0]
                        patch_bytecode = assemble_code('b%s %s\nb %s'%(jump_token, hex(true_jump_unsigned_offset), hex(false_jump_unsigned_offset)),it_ins_addr)
                        if len(patch_bytecode) > it_block_len:
                            print(f'Patch Block Over {len(patch_bytecode) - it_block_len} Bytecode Length Warning!!!')
                        else:
                            original_bytecode = bv.read(it_ins_addr, it_block_len)
                            print('Replacing %s with %s at %s' % (original_bytecode.hex(), patch_bytecode.hex(), hex(it_ins_addr)))
                            patch = (it_ins_addr, patch_bytecode)
                            patch_obj = { f'b{jump_token} %s\nb %s': (it_ins_addr, true_block_address, false_block_address)}
                            patch_data.append(patch)
                            patch_objs.append(patch_obj)
                    else:
                        print('not end condition, need check what todo')
                        print(hex(asm_basic_block.start))
                else:
                    print('not found it condition')
                    exit

            # print('%s, %s' %(hex(asm_basic_block.start), last_ins.tokens[0].text.startswith('b')))
    return patch_data, patch_objs

def save_patch(patch_data: List[Tuple['int', 'bytes']]):
    for addr, bytecode in patch_data:
        bv.write(addr, bytecode)

def get_ssa_cff_nodes(func: Function) -> List['MediumLevelILBasicBlock']:
    mlil_ssa = func.mlil.ssa_form
    cff_nodes = []
    for block in mlil_ssa.basic_blocks:
        count = 0
        for edge in block.incoming_edges:
            if block in edge.source.dominators:
                count += 1
        if count >= 3:
            cff_nodes.append(block)
    return cff_nodes

# def parse_phi_list(base_var: SSAVariable, phi_ins_list: List['MediumLevelILVarPhi']) -> MediumLevelILInstruction:
#     # graph = {}
#     # for phi_ins in phi_ins_list:
#     #     phi_dest_var = phi_ins.dest
#     #     if phi_dest_var not in graph:
#     #         graph[phi_dest_var] = phi_ins.src
#     max_phi_ins=phi_ins_list[0]
#     for phi_ins in phi_ins_list:
#         if len(max_phi_ins.src) < len(phi_ins.src):
#             max_phi_ins = phi_ins
#     return max_phi_ins
            

def get_phi_ins(cff_node: MediumLevelILBasicBlock) -> 'MediumLevelILVarPhi':
    # get if instruction
    mlil_func = cff_node.il_function
    instructions = list(mlil_func.instructions)
    phi_ins = None
    for ins in instructions[cff_node.start: cff_node.end]:
        if isinstance(ins, MediumLevelILIf):
            cond_ins = ins.condition
            if isinstance(cond_ins, MediumLevelILVarSsa):
                # find defination
                cond_var_def_ins = mlil_func.get_ssa_var_definition(cond_ins)
                possible_phi_ins = mlil_func.get_ssa_var_definition(cond_var_def_ins.src.left)
                # print(possible_phi_ins)
                if isinstance(possible_phi_ins, MediumLevelILVarPhi):
                    phi_ins = possible_phi_ins
            elif isinstance(cond_ins, (MediumLevelILCmpE, MediumLevelILCmpNe, MediumLevelILCmpSgt, MediumLevelILCmpSle)):
                # print('%s in %s' % (type(cond_ins), cond_ins))
                # print('%s in %s' % (type(cond_ins.left), cond_ins.left))
                cond_var = cond_ins.left
                if isinstance(cond_var, MediumLevelILVarSsa):
                    possible_phi_ins = mlil_func.get_ssa_var_definition(cond_var)
                    if not isinstance(possible_phi_ins, MediumLevelILVarPhi):
                        if (possible_phi_ins.dest == cond_var.var):
                            # print(possible_phi_ins)
                            # this meant var assign from others
                            from_var = possible_phi_ins.src
                            # print(from_var)
                            possible_phi_ins = mlil_func.get_ssa_var_definition(from_var)
                            # below is find compare phi-node
                            # all_use_inss = list(filter(lambda x: isinstance(x, MediumLevelILVarPhi) and cond_var.var in x.vars_read+x.vars_written, mlil_func.get_ssa_var_uses(cond_var)))
                            # possible_phi_ins = parse_phi_list(cond_var, all_use_inss)
                        else:
                            print('error from get_phi_ins')

                elif isinstance(cond_var, MediumLevelILVarSsaField):
                    possible_phi_ins = mlil_func.get_ssa_var_definition(cond_var.src)
                    # print(cond_var.src)
                else:
                    print('todo in get_phi_ins')
                if isinstance(possible_phi_ins, MediumLevelILVarPhi):
                    phi_ins = possible_phi_ins
            else:
                print('Unknown condition type: %s in %s' % (type(cond_ins), cond_ins))
    # if phi_ins is None:
    #     print('Failed to find phi instruction, stop working!')
    return phi_ins

def get_ssa_node_state_var(phi_ins: MediumLevelILVarPhi, blocks: List['MediumLevelILBasicBlock']) -> Dict['MediumLevelILBasicBlock','ConstantRegisterValue']:
    # get if instruction
    mlil_func = phi_ins.il_basic_block.il_function.ssa_form
    instructions = list(mlil_func.instructions)
    # find all state
    state_var_defs = {}
    for block in blocks:
        for ins in instructions[block.start: block.end]:
            if isinstance(ins, MediumLevelILSetVarSsa) and isinstance(ins.src, MediumLevelILConst):
                # check dest SSAVariable is in Phi src
                # ret = is_state_var(phi_ins, ins.dest)
                # print('%s: %s' % (ins, ret))
                if is_state_var(phi_ins, ins.dest):
                    state_var_defs[block] = ins.src.value
            # elif isinstance(ins, MediumLevelILSetVarSsaField):
            #     ret = is_state_var(phi_ins, ins.dest)
            #     print('%s: %s' % (ins, ret))
    return state_var_defs

def cleanup_bogus_code(func: Function):
    mlil_ssa = func.mlil.ssa_form
    mlil_instructions = list(mlil_ssa.instructions)
    # print(mlil_instructions)
    # get all determined code
    cfg_links = []
    for block in mlil_ssa.basic_blocks:
        source_block = block.source_block
        for mlil_ins in mlil_instructions[block.start: block.end]:
            if isinstance(mlil_ins, MediumLevelILIf) and isinstance(mlil_ins.condition, MediumLevelILConst):
                # print('%s, %s' % (mlil_ins.condition.constant, type(mlil_ins.condition.constant)))
                cond_int = mlil_ins.condition.constant
                # print(block.outgoing_edges)
                out_edge1, out_edge2 = block.outgoing_edges
                print(block.outgoing_edges)
                if out_edge1.type == BranchType.TrueBranch:
                    true_block, false_block = out_edge1.target,out_edge2.target
                else:
                    false_block, true_block = out_edge2.target, out_edge1.target

                if cond_int:
                    # means true
                    link = (source_block, true_block)
                else:
                    # means false
                    link = (source_block, false_block)
                cfg_links.append(link)
    patches = generate_patch(cfg_links)
    # print(cfg_links)
    save_patch(patches)
    



# def get_cond_map(func: Function):
#     cond_map = {}
#     for block in func.mlil:
#         # print(block)
#         ret = get_if_cond(block, const_map_handler)
#         if ret is not None:
#             print(ret)
#         for ins in list(block.il_function.instructions)[block.start: block.end]:
#                 if isinstance(ins.condition, (MediumLevelILCmpE, MediumLevelILCmpNe)) and isinstance(ins.condition.right, MediumLevelILConst):
#                     ret_map = (get_const_map([ins]))
#                     print(ret_map)
#     return cond_map

# def get_if_cond(block: MediumLevelILBasicBlock, callback: Callable[[MediumLevelILSetVar, MediumLevelILIf], Any] ):
#     cond_var = None
#     for ins in list(block.il_function.instructions)[block.start: block.end]:
#         if isinstance(ins, MediumLevelILSetVar):
#             if (ins.dest.name.startswith('cond')):
#                 # print(type(ins.src))
#                 cond_var = ins
#         if isinstance(ins, MediumLevelILIf):
#             if cond_var is not None and cond_var.dest == ins.condition.var:
#                 return callback(cond_var, ins)

# def const_map_handler(cond_var: MediumLevelILSetVar, if_cond: MediumLevelILIf):
#     if (cond_var.src.operation == MediumLevelILOperation.MLIL_CMP_E):
#         target_block = if_cond.true
#     elif cond_var.src.operation == MediumLevelILOperation.MLIL_CMP_NE:
#         target_block = if_cond.false
#     return target_block, cond_var, if_cond

# def state_var_handler(cond_var: MediumLevelILSetVar, if_cond: MediumLevelILIf):
#     if isinstance(cond_var.src.left, MediumLevelILVar):
#         return cond_var.src.left.var
import array
import pickle

def write_array(array):
    with open('/tmp/patch_obj.pickle', 'wb') as file:
        pickle.dump(array, file)

if __name__ == "__main__":

    try:
        timeout = 30
        target = "libnative-lib.so"

        import binaryninja
        bv = binaryninja.load(target)
        print("Analyzing file: {}".format(target))
        bv.add_analysis_option('linearsweep')
    except:
        entry_name = ''
    finally:
        entry_name = 'JNI_OnLoad'
        # entry_name = 'sub_12ae4'
        # entry_name = 'sub_17f9c'
    func_addr = 0x00010ba8
    # func = bv.get_functions_by_name(entry_name)[0]
    func = bv.get_function_at(func_addr)



    ssa_cff_nodes = get_ssa_cff_nodes(func)
    ssa_cff_nodes.reverse()
    # print(len(ssa_cff_nodes))
    data_to_patch = []
    # for ssa_cff_node in ssa_cff_nodes[25:26]:
    for ssa_cff_node in ssa_cff_nodes[:5]:
        # state_var = get_state_var(conditions)
        print(ssa_cff_node)
        phi_ins = get_phi_ins(ssa_cff_node)
        if phi_ins is None:
            print('Not Found Phi Node, skipping to next')
            print()
            continue
        print(phi_ins)
        warn_list = replace_phi_def_var(ssa_cff_node)
        if len(warn_list) > 0:
            print(warn_list)
            exit
        child_blocks = get_dom_child_blocks(ssa_cff_node)
        conditions = get_conds_in_blocks(phi_ins, child_blocks)
        state_var_defs = get_ssa_node_state_var(phi_ins, child_blocks)
        const_dict = get_const_map(conditions, state_var_defs)
        cfg_links = generate_cfg(const_dict, state_var_defs)
        # cfg_links = list(filter(lambda x: len(x)==2, cfg_links))
        patches, patch_objs = generate_patch(cfg_links, func)
    #     save_patch(patches)
    #     # print('\n'.join('%s: %s' % (hex(a), p.hex()) for a, p in (patches)))
        # for link in cfg_links:
        #     if len(link) == 2:
        #         # print('%s: %s' %(hex(link[0].start), link[1]))
        #         print()
        #     else:
        #         print('%s: %s, %s' %(hex(link[0].start), link[1], link[2]))
        # print(len(patches))
        # print(cfg_links[14])
        # print(len(cfg_links))
        # print(state_var_defs)
    #     # print(child_blocks)
        # print(conditions)
        # print('\n'.join('%s: %s'%(k, d) for k, d in const_dict.items()))
    # # clean up bogus code
    # func = bv.get_functions_by_name(entry_name)[0]
    # func = bv.get_function_at(func_addr)
    # cleanup_bogus_code(func)
        # print(patch_objs)
        data_to_patch.append(patch_objs)
        print()

    write_array(data_to_patch)
        

    # # for func in bv.functions:
    # #     if func.name != entry_name: continue
    # #     print("Function: {}".format(func.name))
    # #     for block in func.medium_level_il.ssa_form:
    # #         for instr in block:
    # #             print(instr)
    # #             print(type(instr))
    # func = bv.get_functions_by_name(entry_name)[0]
    # for inss in func.medium_level_il.ssa_form.instructions:
    #     # if inss.operation == MediumLevelILOperation.MLIL_SET_VAR_SSA:
    #     if isinstance(inss, MediumLevelILSetVarSsa):
    #         if inss.dest.name.startswith('cond:'):
    #             print(f"{hex(inss.address)} : {inss}")
    #             if isinstance(inss.src, (MediumLevelILCmpE, MediumLevelILCmpNe)):
    #                 comp_inss = inss.src
    #                 # vars: MediumLevelILVarSsa = comp_inss.left
    #                 vars: HighLevelILVarInit = comp_inss.left
    #                 vars.src
    #                 print(f"{type(vars)}")
    #                 print(f"{(vars.src.name)}")
    #     # if isinstance(inss, MediumLevelILIf):
    #     #     print(f"{hex(inss.address)} : {inss}")

