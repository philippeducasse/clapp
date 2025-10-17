import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { capitalize } from "lodash";
const statusBadgeVariants = cva(
  "inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      status: {
        [ApplicationStatus.NOT_APPLIED]:
          "border-transparent bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
        [ApplicationStatus.APPLIED]:
          "border-transparent bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
        [ApplicationStatus.IN_DISCUSSION]:
          "border-transparent bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
        [ApplicationStatus.REJECTED]:
          "border-transparent bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
        [ApplicationStatus.IGNORED]:
          "border-transparent bg-gray-300 text-gray-800 dark:bg-gray-600 dark:text-gray-400",
        [ApplicationStatus.ACCEPTED]:
          "border-transparent bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
        [ApplicationStatus.POSTPONED]:
          "border-transparent bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
        [ApplicationStatus.CANCELLED]:
          "border-transparent bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
        [ApplicationStatus.OTHER]:
          "border-transparent bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-400",
      },
    },
    defaultVariants: {
      status: ApplicationStatus.NOT_APPLIED,
    },
  }
);

interface StatusBadgeProps
  extends React.ComponentProps<"span">,
    VariantProps<typeof statusBadgeVariants> {
  status: ApplicationStatus;
}

function StatusBadge({ className, status, ...props }: StatusBadgeProps) {
  const formatStatus = (status: ApplicationStatus) => {
    return capitalize(status.replace(/_/g, " "));
  };

  return (
    <span
      data-slot="status-badge"
      className={cn(statusBadgeVariants({ status }), className)}
      {...props}
    >
      {formatStatus(status)}
    </span>
  );
}

export { StatusBadge, statusBadgeVariants };
