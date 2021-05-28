{ pkgs }:
let my-python-packages = python-packages: with python-packages; [ pipx ];
in pkgs.mkShell {
  buildInputs = with pkgs; [
    (python3.withPackages my-python-packages)
    solc
    nodejs
    yarn
  ];
  shellHook = ''
    export PATH="$HOME/.local/bin:$PATH"
    if [ ! -f "$(which brownie)" ]; then
      pipx install eth-brownie
    fi
  '';
}
