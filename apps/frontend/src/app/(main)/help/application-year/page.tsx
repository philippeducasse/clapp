/* eslint-disable react/no-unescaped-entities */
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar } from "lucide-react";

export default function ApplicationYearHelpPage() {
  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-emerald-700 mb-2">Application Year</h1>
        <p className="text-gray-600">Specify which year or season you're focusing your applications on</p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-emerald-600" />
              What does this do?
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700 space-y-3">
            <p>
              Set the year or season you're currently applying for. This helps you stay organized when
              applying across multiple years.
            </p>
            <div className="bg-blue-50 p-3 rounded space-y-2 text-sm">
              <p className="font-semibold">Examples:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>It's September 2026, but you want to apply for 2027 → enter 2027</li>
                <li>You're applying for 2026 this year → enter 2026</li>
                <li>Leave blank to default to the current year</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        <div className="text-sm text-gray-600 bg-gray-50 p-4 rounded">
          <p>
            <strong>Note:</strong> This field is important as it is checked when sending out applications: if there is aleady an application for the organisation for the same year, the application will be blocked.
          </p>
        </div>

        <Button asChild className="w-full">
          <Link href="/profile/edit/preferences">Go to Preferences</Link>
        </Button>
      </div>
    </div>
  );
}