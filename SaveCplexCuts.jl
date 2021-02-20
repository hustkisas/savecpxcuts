module SaveCplexCuts

export save_cpx_cuts, solve_root_node, remove_const_from_obj, parse_save_cpx_cuts

using CPLEXW, JuMP, JSON

function solve_callback(env, cbdata, wherefrom, cbhandle, useraction_p) :: Int32
        @info "inside solve_callback"
        nodelp_p = [CPXLPptr(0)]
        CPXgetcallbacknodelp(env, cbdata, wherefrom, nodelp_p);
        CPXwriteprob(env, nodelp_p[1], "./cuts/rootnodemodel.mps", C_NULL);
        return 0
end 

c_solve_callback = @cfunction(solve_callback, Cint, (
        CPXENVptr,  # env
        Ptr{Cvoid}, # cbdata
        Cint,       # wherefrom
        Ptr{Cvoid}, # cbhandle
        Ptr{Cint},  # useraction_p
    ))

"""
    solve_root_node(file_name::String)

read a MPS file, solve at root node, and save the root node LP that has CPLEX cuts added.
Note that, the file_name should be discoverable by the program. 

# Examples
```julia-repl
julia> solve_root_node('./test.MPS')
1
```
"""


function solve_root_node(file_name::String)

    status_p = [Cint(0)]
    env = CPXopenCPLEX(status_p)
    CPXsetintparam(env, CPX_PARAM_SCRIND, CPX_ON) # Print to the screen
    CPXsetdblparam(env, CPX_PARAM_NODELIM, 0)      # MIP node limit
    #CPXsetdblparam(env, CPX_PARAM_CUTSFACTOR, 0)  # Disable cutting planes
    #CPXsetintparam(env, CPX_PARAM_PREIND, 0)      # Disable preprocessing
    #CPXsetintparam(env, CPX_PARAM_HEURFREQ, -1)   # Disable primal heuristics
    lp = CPXcreateprob(env, status_p, "problem")
    CPXreadcopyprob(env, lp, file_name, "mps")
    CPXsetsolvecallbackfunc(env, c_solve_callback, C_NULL)
    CPXmipopt(env, lp);

    @info "Root node solution is done! "
    
end    

"""
    parse_save_cpx_cuts(file_name::String)

read the MPS file saved by solve_root_node(), parse the CPLEX cuts, and save cuts into JSON files. 

# Examples
```julia-repl
julia> solve_root_node('./test.MPS')
1
```
"""

function parse_save_cpx_cuts(file_name::String)
    m = JuMP.read_from_file("./cuts/rootnodemodel.mps");
    @info "JuMP read $(file_name) successfully."
#        write_to_file(m, string(input_file_path, inputfiles[1], ".lp");format = MOI.FileFormats.FORMAT_LP)
    cons = all_constraints(m, GenericAffExpr{Float64,VariableRef}, MOI.LessThan{Float64});
    #cons = [all_constraints(m, GenericAffExpr{Float64,VariableRef}, MOI.LessThan{Float64});all_constraints(m, GenericAffExpr{Float64,VariableRef}, MOI.EqualTo{Float64});all_constraints(m, GenericAffExpr{Float64,VariableRef}, MOI.GreaterThan{Float64})];

    ib_json_dict = Dict{String, Any}("file name" => file_name)
    mir_json_dict = Dict{String, Any}("file name" => file_name)
    f_json_dict = Dict{String, Any}("file name" => file_name)
    dir_name = "./cuts/"
    ib_cut_file = open(string(dir_name,file_name,"_ib.json"), "a"); 
    mir_cut_file = open(string(dir_name,file_name,"_mir.json"), "a");
    f_cut_file = open(string(dir_name,file_name,"_f.json"), "a");
    @info "Start parsing cuts"
    cnt_ib = 0; cnt_mir = 0; cnt_f =0;
    for conRef in cons
        if name(conRef)[begin] in ['i','f','m', 'r'] && isdigit(name(conRef)[begin+1])
            @info name(conRef)
            c = constraint_object(conRef)
            cut_name = name(conRef)
            dict = Dict(name(key)=> val for (key,val) in c.func.terms)
            dict["rhs"] = c.func.constant

            if name(conRef)[begin] == 'i' && isdigit(name(conRef)[2]) # implied bound cuts
                ib_json_dict[cut_name] = dict
                cnt_ib ++;
            elseif name(conRef)[begin] == 'm' && isdigit(name(conRef)[2])
                mir_json_dict[cut_name] = dict
                cnt_mir ++; 
            else name(conRef)[begin] == 'f' && isdigit(name(conRef)[2])
                f_json_dict[cut_name] = dict
                cnt_f ++;
            end
        end
    end
    @info "Finished parsing. $(cnt_ib) implied bound cuts; $(cnt_mir) MIR cuts; $(cnt_f) flow cover cuts."
    write(ib_cut_file, JSON.json(ib_json_dict));                                            
    write(mir_cut_file, JSON.json(mir_json_dict));                                                
    write(f_cut_file, JSON.json(f_json_dict));
    close(ib_cut_file)     
    close(mir_cut_file)
    close(f_cut_file)
end    
          
"""
    remove_const_from_obj(file_name::String)

After CPLEX solves the model at root node, it might result in an objective function with a constant term, which will cause an error when JuMP tries to read the MPS file. This function remove the line in MPS file to remove the constant term in the objective function.

# Examples 
```julia-repl
julia> remove_const_from_obj("rootnodemodel.mps");

```
"""
function remove_const_from_obj(file_name::String)
    data = open(io -> String(read(io)), file_name);
    range = findfirst(r"RHS\n[^\n]*obj[^\n]*\n", data)
    if range === nothing
        @info "Objective function does not have a constrant."
        return nothing
    end
    open(file_name, "w") do writer
        write(writer, SubString(data,1:first(range)+3))
        write(writer, SubString(data,last(range)+1:lastindex(data)))
    end
    @info "Objective function has a constant and it has been removed."


end




function save_cpx_cuts(file_name::String)
    if !isdir("./cuts")
        mkdir("cuts")                                                            
    end
    solve_root_node(file_name)
    remove_const_from_obj("./cuts/rootnodemodel.mps")
    parse_save_cpx_cuts(file_name)

end

end 