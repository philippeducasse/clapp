import StoreProvider from "@/redux/StoreProvider";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <StoreProvider>
      <div className="flex min-h-screen mt-24 justify-center bg-background">
        <div className="">
          <div className="flex justify-center gap-4 text-emerald-600">
            <h1 className="font-clapp text-4xl">Clapp</h1>
            <img src={"/logo.png"} width={60} height={60} alt="Clapping hands" />
          </div>
          <div className="w-full max-w-lg p-8">{children}</div>
        </div>
      </div>
    </StoreProvider>
  );
}
