import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/profiles/:path*",
        destination: "http://localhost:8000/api/profiles/:path*/",
      },
    ];
  },
};

export default nextConfig;
