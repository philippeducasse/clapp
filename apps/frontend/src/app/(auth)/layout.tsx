import StoreProvider from "@/redux/StoreProvider";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <StoreProvider>
      {children}
    </StoreProvider>
  );
}
