import StoreProvider from "@/redux/StoreProvider";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <StoreProvider>
      <div className="flex min-h-screen mt-24 justify-center bg-background">
        <div className="w-full max-w-lg p-8">{children}</div>
      </div>
    </StoreProvider>
  );
}
