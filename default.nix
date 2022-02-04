{ pkgs ? import <nixpkgs> {} }:

pkgs.poetry2nix.mkPoetryApplication {
  projectDir = ./.;
  overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: {
      py-cui = super.py-cui.overridePythonAttrs (attrs: {
        patches = [
	   ./py_cui_setup.patch
        ];
      });
    });
}
