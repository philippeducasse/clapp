import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
    console.log("🔧 Next.js rewrites using BACKEND_URL:", backendUrl);
    return [
      {
        source: "/api/:path(.*)",
        destination: `${backendUrl}/api/:path/`,
      },
    ];
  },
};

export default nextConfig;
