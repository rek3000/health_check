{ pkgs ? import <nixpkgs> {} }:
(pkgs.buildFHSUserEnv {
  name = "rekdoc";
  targetPkgs = pkgs: (with pkgs; [
    python3
    python312Packages.pip
    python312Packages.virtualenv
    zlib
  ]);
  runScript = "bash";
}).env
