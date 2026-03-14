import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {
    // Force project root to admin-panel to avoid parent workspace lockfile detection.
    root: __dirname,
  },
};

export default nextConfig;
