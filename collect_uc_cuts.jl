include("SaveCplexCuts.jl")
using .SaveCplexCuts
cd("./Data/case1888rte/")
file_list = readdir()

for file_name in file_list
	if occursin("final.mps.gz", file_name) 
		save_cpx_cuts(file_name)
	end 
end 

