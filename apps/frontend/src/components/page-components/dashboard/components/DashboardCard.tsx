import { Card, CardHeader, CardDescription, CardTitle, CardContent } from "@/components/ui/card";
import React from "react";

export interface DashboardCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
}

const DashboardCard = ({ title, value, subtitle }: DashboardCardProps) => {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="text-2xl"> {title}</CardDescription>
        <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xl text-muted-foreground">{subtitle}</p>
      </CardContent>
    </Card>
  );
};

export default DashboardCard;
