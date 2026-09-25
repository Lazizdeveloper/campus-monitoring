{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    uv
    python312Packages.playwright
    python312Packages.pytest
  ];

  shellHook = ''
    export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
    export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
    export PLAYWRIGHT_NODEJS_PATH=${pkgs.nodejs}/bin/node
    echo "Bot muhiti tayyor! Ishga tushirish uchun: uv run campus-monitoring"
  '';
}
