/* eslint-disable react/no-unescaped-entities */
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, FileText } from "lucide-react";
import {
  ExcelFormatTable,
  ImportStepsGuide,
  ExampleExcelTable,
} from "@/components/page-components/upload/uploadHelper";

export default function ImportingOrganizationsHelpPage({
  showGoToUploadPage = true,
}: {
  showGoToUploadPage: boolean;
}) {
  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-emerald-700 mb-2 mt-4">Importing Organizations</h1>
        <p className="text-gray-600 text-lg">
          Bulk import festivals, venues, and residencies from an Excel file
        </p>
      </div>

      <div className="space-y-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              What is Bulk Import?
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700 space-y-3">
            <p>
              Instead of creating organizations one-by-one, you can import multiple festivals,
              venues, and residencies at once using an Excel file. This is perfect for building your
              database quickly if you already have a list of organizations.
            </p>
            <p>
              The system will automatically detect the organization type and create new entries in
              your database.
            </p>
          </CardContent>
        </Card>

        <ExcelFormatTable />

        <ImportStepsGuide />

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
              Data Requirements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Required Fields</h4>
              <p className="text-gray-600 text-sm">
                Each organization must have at least these three pieces of information:
              </p>
              <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside ml-2 mt-2">
                <li>
                  <strong>Type</strong> - Must be "Festival", "Venue", or "Residency"
                </li>
                <li>
                  <strong>Name</strong> - The organization name
                </li>
                <li>
                  <strong>Country</strong> - Where the organization is located
                </li>
              </ul>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <h4 className="font-semibold text-gray-900 mb-2">Invalid Entries</h4>
              <p className="text-gray-600 text-sm">
                Organizations with missing required fields will be skipped during import. You'll see
                a report showing which rows had errors. You can then create these manually or update
                your Excel file and try again.
              </p>
            </div>
            <div className="border-t border-gray-200 pt-4">
              <h4 className="font-semibold text-gray-900 mb-2">Repeated entries</h4>
              <p className="text-gray-600 text-sm">
                Organizations already registered in the database will be also skipped during import.
              </p>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <h4 className="font-semibold text-gray-900 mb-2">File Size Limit</h4>
              <p className="text-gray-600 text-sm">
                Excel files should be under 10MB. If your file is larger, split it into multiple
                files and upload them separately.
              </p>
            </div>
          </CardContent>
        </Card>
        <ExampleExcelTable />
        {showGoToUploadPage && (
          <Card className="border-l-4 border-l-emerald-500 bg-emerald-50">
            <CardHeader>
              <CardTitle>Ready to Import?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-700">
                Once you've prepared your Excel file, head to the Upload page to import your
                organizations.
              </p>
              <Button asChild className="w-full md:w-auto">
                <Link href="/upload">Go to Upload Page</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
