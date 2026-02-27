import React from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

const ConfirmationMessage = () => {
  const searchParams = useSearchParams();
  const status = searchParams.get("status");
  const message = searchParams.get("message");

  const isSuccess = status === "success";

  return (
    <div className="text-center space-y-6">
      {isSuccess ? (
        <>
          <div className="text-emerald-600">
            <svg
              className="w-16 h-16 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-foreground">Email Confirmed!</h2>
          <p className="text-muted-foreground">
            Your email has been successfully confirmed. You can now log in to your account.
          </p>
        </>
      ) : (
        <>
          <div className="text-red-600">
            <svg
              className="w-16 h-16 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-foreground">Confirmation Failed</h2>
          <p className="text-muted-foreground">
            {message === "invalid_token"
              ? "The confirmation link is invalid or has expired. Please request a new confirmation email."
              : "An error occurred while confirming your email. Please try again."}
          </p>
        </>
      )}

      <Link
        href={isSuccess ? "/login" : "/register"}
        className="inline-block mt-8 px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
      >
        {isSuccess ? "Go to Login" : "Back to Registration"}
      </Link>
    </div>
  );
};

export default ConfirmationMessage;
