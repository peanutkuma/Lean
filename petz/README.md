# Useful tips and tricks when running LEAN engine

## Setting up Lean with Python support  :

* clone Lean

* Follow the README.md instructions to install and configure mono, and the various python dependencies

* To build the csharp solution execute:

  `msbuild Lean/QuantConnect.Lean.sln`

* To configure python, install conda with python 3.6.8 and also install `pip install
  qunatconnect-stubs` . Then configure Lean to discover python runtime library by ediginng the file
  `Lean/Common/Python/Python.Runtime.dll.config`. You need to add this line

```xml
<dllmap os="linux" dll="python3.6m" target = "/home/kenny/software/anaconda3/envs/lean/lib/libpython3.6m.so"/>
```

* To run your first python algo execute the script `./run.sh` (from the current directory). It should work out of the box






