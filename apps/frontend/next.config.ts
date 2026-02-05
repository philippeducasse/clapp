import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    unoptimized: true,
  },
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    console.log(
      "🔧 Next.js rewrites using NEXT_PUBLIC_BACKEND_URL:",
      process.env.NEXT_PUBLIC_BACKEND_URL,
    );
    return [
      {
        source: "/api/:path(.*)",
        destination: `${backendUrl}/api/:path/`,
      },
    ];
  },
};

export default nextConfig;
