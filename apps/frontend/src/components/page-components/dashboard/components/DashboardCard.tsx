import { Card, CardHeader, CardDescription, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import React from "react";

export interface DashboardCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  loading?: boolean;
}

const DashboardCard = ({ title, value, subtitle, loading }: DashboardCardProps) => {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="text-2xl"> {title}</CardDescription>
        <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">
          {loading ? <Skeleton className="h-6 mt-2 w-full" /> : value}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xl text-muted-foreground text-right">{subtitle}</p>
      </CardContent>
    </Card>
  );
};

export default DashboardCard;
