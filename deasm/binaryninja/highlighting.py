
func = current_function.mlil.ssa_form

instr = list(func.instructions)[38]

x21_uses=func.get_ssa_var_uses(instr.dest)

arg_defs = func.get_ssa_var_definition(instr.src)

for var in x21_uses:current_function.set_auto_instr_highlight(var.address, HighlightColor(HighlightStandardColor.YellowHighlightColor))

for var in x21_uses:
    current_function.set_auto_instr_highlight(var.address, HighlightColor(HighlightStandardColor.YellowHighlightColor))

for arg in arg_defs.src:
    arg_def = func.get_ssa_var_definition(arg)
    if arg_def is None:
        continue
    if type(arg_def.src) is not MediumLevelILVarSsa:
        current_function.set_auto_instr_highlight(arg_def.address, HighlightColor(HighlightStandardColor.RedHighlightColor))
        
