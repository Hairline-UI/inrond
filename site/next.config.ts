import type { NextConfig } from "next";

// The page has no server work: export it as static files.
const config: NextConfig = {
  output: "export",
  images: { unoptimized: true },
  trailingSlash: false,
};

export default config;
