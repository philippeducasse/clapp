import * as React from "react";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { TagAction } from "@/interfaces/Enums";
import { Star, Eye, TriangleAlert, X, CircleQuestionMark } from "lucide-react";

const tagBadgeVariants = cva(
  "inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      tag: {
        [TagAction.STAR]:
          "border-transparent bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
        [TagAction.WATCH]:
          "border-transparent bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
        [TagAction.WARNING]:
          "border-transparent bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
        [TagAction.INACTIVE]:
          "border-transparent bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
        [TagAction.OTHER]:
          "border-transparent bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
      },
    },
  }
);

const TAG_ICONS = {
  [TagAction.STAR]: Star,
  [TagAction.WATCH]: Eye,
  [TagAction.WARNING]: TriangleAlert,
  [TagAction.INACTIVE]: X,
  [TagAction.OTHER]: CircleQuestionMark,
};

interface TagBadgeProps extends React.ComponentProps<"span"> {
  tag?: string;
}

function TagBadge({ className, tag, ...props }: TagBadgeProps) {
  if (!tag) return null;

  const Icon = TAG_ICONS[tag as TagAction];

  return (
    <span
      data-slot="tag-badge"
      className={cn(tagBadgeVariants({ tag: tag as TagAction }), className)}
      {...props}
    >
      {Icon && <Icon />}
    </span>
  );
}

export { TagBadge, tagBadgeVariants };
