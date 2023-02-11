{
  description = "A Toaq translation of Minecraft";

  inputs.toaq-fonts.url = github:toaq/fonts;
  inputs.nixpkgs.follows = "toaq-fonts/nixpkgs";
  inputs.flake-utils.follows = "toaq-fonts/flake-utils";

  outputs = { self, nixpkgs, flake-utils, toaq-fonts }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        derani-fonts = toaq-fonts.packages.${system}.derani;
      in {
        defaultPackage = pkgs.stdenvNoCC.mkDerivation {
          name = "huaibai";
          src = self;
          buildInputs = [ pkgs.zip ];
          buildPhase = ''
            cp -r src build
            cp ${derani-fonts}/share/fonts/opentype/Guezueq.otf \
              build/assets/minecraft/textures/font/guezueq.otf
            cd build
            zip -r ../Huaıbaı.zip *
            cd ..
          '';
          installPhase = ''
            mkdir $out
            mv Huaıbaı.zip $out/
          '';
        };
      }
    );
}
