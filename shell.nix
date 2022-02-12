{ pkgs ? import <nixpkgs> {} }:
let
  lazydokku = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    editablePackageSources = {
      my-app = ./lazydokku;
    };
    overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
      py-cui = super.py-cui.overridePythonAttrs (attrs: {
        patches = [
          ./py_cui_setup.patch
        ];
      });
    });
  };
in lazydokku.env
