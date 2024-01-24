{ pkgs ? import <nixpkgs> {} }:
(pkgs.buildFHSUserEnv {
  name = "rekdoc";
  targetPkgs = pkgs: (with pkgs; [
    python3
    python311Packages.pip
    python311Packages.virtualenv
    zlib
  ]);
  runScript = "bash";
}).env
