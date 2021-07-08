{ pkgs }:
let my-python-packages = python-packages: with python-packages; [ pipx pip ];
in pkgs.mkShell {
  buildInputs = with pkgs; [
    (python3.withPackages my-python-packages)
    nodejs
    yarn
  ] ++ (pkgs.lib.optionals pkgs.stdenv.isLinux [solc]);
  shellHook = ''
    export PATH="$HOME/.local/bin:./node_modules/.bin:$PATH"
    pipx install eth-brownie
  '';
}
