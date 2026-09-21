import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { TagAction } from "@/interfaces/Enums";
import { Star, Eye, TriangleAlert, X, CircleQuestionMark, EyeOff } from "lucide-react";
import { Badge } from "../ui/badge";

const tagBadgeVariants = cva("text-md [&>svg]:size-4", {
  variants: {
    tag: {
      [TagAction.STAR]:
        "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800/40",
      [TagAction.WATCH]:
        "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800/40",
      [TagAction.WARNING]:
        "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400 border-orange-200 dark:border-orange-800/40",
      [TagAction.INACTIVE]:
        "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600",
      [TagAction.IRRELEVANT]:
        "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600",
      [TagAction.OTHER]:
        "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200 dark:border-purple-800/40",
    },
  },
});

const TAG_ICONS = {
  [TagAction.STAR]: Star,
  [TagAction.WATCH]: Eye,
  [TagAction.WARNING]: TriangleAlert,
  [TagAction.INACTIVE]: X,
  [TagAction.IRRELEVANT]: EyeOff,
  [TagAction.OTHER]: CircleQuestionMark,
};

interface TagBadgeProps extends React.ComponentProps<"span"> {
  tag?: string;
}

function TagBadge({ className, tag, ...props }: TagBadgeProps) {
  if (!tag) return null;

  const Icon = TAG_ICONS[tag as TagAction];

  return (
    <Badge
      data-slot="tag-badge"
      className={cn(tagBadgeVariants({ tag: tag as TagAction }), className)}
      {...props}
    >
      {Icon && <Icon />}
    </Badge>
  );
}

export { TagBadge, tagBadgeVariants };
