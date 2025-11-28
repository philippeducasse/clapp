export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen mt-24 justify-center bg-background">
      <div className="w-full max-w-lg p-8">{children}</div>
    </div>
  );
}
