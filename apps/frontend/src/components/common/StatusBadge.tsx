import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { capitalize } from "lodash";
import { Badge } from "../ui/badge";
const statusBadgeVariants = cva(
  "",
  {
    variants: {
      status: {
        [ApplicationStatus.NOT_APPLIED]:
          "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600",
        [ApplicationStatus.APPLIED]:
          "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800/40",
        [ApplicationStatus.IN_DISCUSSION]:
          "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200 dark:border-purple-800/40",
        [ApplicationStatus.REJECTED]:
          "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800/40",
        [ApplicationStatus.IGNORED]:
          "bg-gray-300 text-gray-800 dark:bg-gray-600 dark:text-gray-400 border-gray-400 dark:border-gray-500",
        [ApplicationStatus.ACCEPTED]:
          "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800/40",
        [ApplicationStatus.POSTPONED]:
          "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800/40",
        [ApplicationStatus.CANCELLED]:
          "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 border-orange-200 dark:border-orange-800/40",
        [ApplicationStatus.OTHER]:
          "bg-slate-100 text-slate-700 dark:bg-slate-900/30 dark:text-slate-400 border-slate-200 dark:border-slate-800/40",
        [ApplicationStatus.DRAFT]:
          "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800/40",
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
    <Badge
      data-slot="status-badge"
      className={cn(statusBadgeVariants({ status }), className)}
      {...props}
    >
      {formatStatus(status)}
    </Badge>
  );
}

export { StatusBadge, statusBadgeVariants };
