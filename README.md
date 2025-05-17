# THIS REPOSITORY IS STILL CURRENTLY A WORK IN PROGRESS!

# Dependencies

My pixel-art scraper is bifurcated into **four** sections:
* *Terraria Mods*
* *Vanilla Terraria*
* *Minecraft Mods*
* *Vanilla Minecraft*

For the **Terraria Mods**, you need the following executables:
* [TML.Patcher](https://github.com/steviegt6/fnb/releases)
* [ILSpyCMD](https://github.com/icsharpcode/ILSpy/releases)

For **Vanilla Terraria**, you need the following executables:
* [ILSpyCMD](https://github.com/icsharpcode/ILSpy/releases) (same as *Terraria Mods*)
* [terrariaxnb2png](https://github.com/Silentspy/terrariaxnb2png/releases)

For the **Minecraft Mods**, you need the following executables:
* [Vineflower](https://github.com/Vineflower/vineflower/releases/tag/1.11.1)

For **Vanilla Minecraft**, you need the following executables:
* [Vineflower](https://github.com/Vineflower/vineflower/releases/tag/1.11.1) (same as *Minecraft Mods*)
* [DecompilerMC](https://github.com/hube12/DecompilerMC)

You will have the opportunity to declare the folder in which you
put all these libraries. Currently, it defaults to a folder named
`lib`. The folder layout for `lib` should look like the following:
```text
.
├── lib
│   ├── TML.Patcher
│   │   ├── TML.Patcher.exe
│   │   └── (...)
│   ├── DecompilerMC
│   │   ├── main.py
│   │   └── (...)
│   ├── ILSpyCMD
│   │   ├── .store
│   │   │   └── (...)
│   │   └── ilspycmd.exe
│   ├── TerrariaXNB2PNG.exe
│   └── vineflower-1.11.1.jar
└── (Your project files)
```
The only caveat is the `ILSpyCMD` doesn't actually have a safe executable
download. Unfortunately, you must download it through `dotnet`. After getting
the latest version of `dotnet`, you must run the following command (as shown
on the ILSPyCMD repository): 

```text
dotnet tool install --global ilspycmd
where ilspycmd (windows) / which ilspycmd (linux)
```

and create a folder called `ILSpyCMD` in the `lib` folder, then copy the executable and the `.store` folder into the `ILSpyCMD`
folder that you just created.
