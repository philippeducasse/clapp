import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, HelpCircle } from "lucide-react";
import { UploadStats } from "./UploadForm";
import { UploadStatCard } from "./UploadStatCard";

export function ExcelFormatTable() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Excel File Format</CardTitle>
        <CardDescription>
          Your Excel file must have these columns (order doesn&apos;t matter)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">Column</th>
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">
                  Required
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">
                  Description
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left font-semibold">
                  Example
                </th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="border border-gray-300 px-4 py-2 font-semibold">Type</td>
                <td className="border border-gray-300 px-4 py-2">
                  <Badge>Required</Badge>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-gray-600">
                  Organization type: Festival, Venue, or Residency
                </td>
                <td className="border border-gray-300 px-4 py-2">Festival</td>
              </tr>
              <tr className="border-b">
                <td className="border border-gray-300 px-4 py-2 font-semibold">Name</td>
                <td className="border border-gray-300 px-4 py-2">
                  <Badge>Required</Badge>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-gray-600">
                  Official name of the organization
                </td>
                <td className="border border-gray-300 px-4 py-2">Global Arts Festival</td>
              </tr>
              <tr className="border-b">
                <td className="border border-gray-300 px-4 py-2 font-semibold">Country</td>
                <td className="border border-gray-300 px-4 py-2">
                  <Badge>Required</Badge>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-gray-600">
                  Country name (full name or ISO code)
                </td>
                <td className="border border-gray-300 px-4 py-2">France</td>
              </tr>
              <tr className="border-b">
                <td className="border border-gray-300 px-4 py-2 font-semibold">Website</td>
                <td className="border border-gray-300 px-4 py-2">
                  <Badge variant="outline">Optional</Badge>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-gray-600">
                  Organization&apos;s website URL
                </td>
                <td className="border border-gray-300 px-4 py-2">www.example.com</td>
              </tr>
              <tr className="border-b">
                <td className="border border-gray-300 px-4 py-2 font-semibold">Date</td>
                <td className="border border-gray-300 px-4 py-2">
                  <Badge variant="outline">Optional</Badge>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-gray-600">
                  Event date (various formats accepted)
                </td>
                <td className="border border-gray-300 px-4 py-2">2025-06-15</td>
              </tr>
              <tr className="border-b">
                <td className="border border-gray-300 px-4 py-2 font-semibold">Email</td>
                <td className="border border-gray-300 px-4 py-2">
                  <Badge variant="outline">Optional</Badge>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-gray-600">
                  Main email address for contact
                </td>
                <td className="border border-gray-300 px-4 py-2">contact@example.com</td>
              </tr>
              <tr className="border-b">
                <td className="border border-gray-300 px-4 py-2 font-semibold">Contact</td>
                <td className="border border-gray-300 px-4 py-2">
                  <Badge variant="outline">Optional</Badge>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-gray-600">
                  Contact person name
                </td>
                <td className="border border-gray-300 px-4 py-2">Jane Smith</td>
              </tr>
              <tr>
                <td className="border border-gray-300 px-4 py-2 font-semibold">Comments</td>
                <td className="border border-gray-300 px-4 py-2">
                  <Badge variant="outline">Optional</Badge>
                </td>
                <td className="border border-gray-300 px-4 py-2 text-gray-600">
                  Additional notes about the organization
                </td>
                <td className="border border-gray-300 px-4 py-2">
                  Great contacts, friendly organizers
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
          <div className="flex gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-blue-900 mb-1">Column Headers Must Match</p>
              <p className="text-sm text-blue-800">
                The column headers in your first row must match the exact names: Type, Name,
                Country, Website, Date, Email, Contact, Comments. The columns can be in any order.
                You can have empty cells for optional fields.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function ImportStepsGuide() {
  const steps = [
    {
      title: "Prepare Your Excel File",
      description:
        "Create an Excel file (.xlsx or .xls) with your organization data. Make sure you follow the format exactly:",
      bullets: [
        "First row contains the column headers (Type, Name, Country, Website, Date, Email, Contact, Comments)",
        "Columns can be in any order - the system reads the headers to match columns",
        "Each subsequent row is one organization",
        'For Type, use: "Festival", "Venue", or "Residency"',
        "Leave cells empty if you don't have data for optional fields",
      ],
    },
    {
      title: "Go to Upload Page",
      description:
        "Navigate to the Upload page in your Clapp dashboard. You can find it in the sidebar menu.",
    },
    {
      title: "Select Your File",
      description:
        "Click the file upload area and select your Excel file. The system will validate the file format before import.",
    },
    {
      title: "Submit and Review",
      description:
        'Click "Upload" to submit your file. The system will process the data and show you a summary of what was imported.',
    },
    {
      title: "Check Results",
      description:
        "You'll see a summary showing how many organizations were imported and if there were any errors. Check your Festivals, Venues, or Residencies pages to see your imported organizations.",
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Step-by-Step Import Guide</CardTitle>
        <CardDescription>Follow these steps to import your organizations</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          {steps.map((step, index) => (
            <div key={index} className={index > 0 ? "border-t border-gray-200 pt-4" : ""}>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">{step.title}</h3>
                  <p className="text-gray-600 mb-3">{step.description}</p>
                  {step.bullets && (
                    <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside ml-2">
                      {step.bullets.map((bullet, bulletIndex) => (
                        <li key={bulletIndex}>{bullet}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function ExampleExcelTable() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Example Excel File</CardTitle>
        <CardDescription>Here&apos;s what your Excel file should look like</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border border-gray-300 px-3 py-2 text-left">Type</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Name</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Country</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Website</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Date</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Email</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Contact</th>
                <th className="border border-gray-300 px-3 py-2 text-left">Comments</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border border-gray-300 px-3 py-2">Festival</td>
                <td className="border border-gray-300 px-3 py-2">Global Arts Festival</td>
                <td className="border border-gray-300 px-3 py-2">France</td>
                <td className="border border-gray-300 px-3 py-2">www.globalarts.fr</td>
                <td className="border border-gray-300 px-3 py-2">2025-06-15</td>
                <td className="border border-gray-300 px-3 py-2">submit@globalarts.fr</td>
                <td className="border border-gray-300 px-3 py-2">Marie Dupont</td>
                <td className="border border-gray-300 px-3 py-2">Contemporary focus</td>
              </tr>
              <tr>
                <td className="border border-gray-300 px-3 py-2">Venue</td>
                <td className="border border-gray-300 px-3 py-2">Modern Dance Studio</td>
                <td className="border border-gray-300 px-3 py-2">Germany</td>
                <td className="border border-gray-300 px-3 py-2">www.moderndance.de</td>
                <td className="border border-gray-300 px-3 py-2"></td>
                <td className="border border-gray-300 px-3 py-2">info@moderndance.de</td>
                <td className="border border-gray-300 px-3 py-2">Hans Mueller</td>
                <td className="border border-gray-300 px-3 py-2"></td>
              </tr>
              <tr>
                <td className="border border-gray-300 px-3 py-2">Residency</td>
                <td className="border border-gray-300 px-3 py-2">European Arts Residency</td>
                <td className="border border-gray-300 px-3 py-2">Spain</td>
                <td className="border border-gray-300 px-3 py-2">www.euarts.es</td>
                <td className="border border-gray-300 px-3 py-2">2025-09-01</td>
                <td className="border border-gray-300 px-3 py-2">applications@euarts.es</td>
                <td className="border border-gray-300 px-3 py-2">Sofia Garcia</td>
                <td className="border border-gray-300 px-3 py-2">3-month program</td>
              </tr>
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

export function ImportHelpCard() {
  return (
    <Card className="mt-6">
      <CardContent className="pt-4">
        <div className="flex gap-3">
          <HelpCircle className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semiboldtext-sm mb-2">Need help formatting your file?</p>
            <p className="text-sm mb-3">
              Learn about the Excel file format and step-by-step import instructions.
            </p>
            <Button asChild variant="outline" size="sm">
              <Link href="/help/importing-organizations">View Import Guide</Link>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function UploadSummarySection({ uploadStats }: { uploadStats: UploadStats }) {
  return (
    <Card className="mt-8 max-w-xl mx-auto">
      <CardTitle className="text-primary text-xl p-4 border-b text-center">
        Upload Summary
      </CardTitle>
      <CardContent className="p-6">
        <div className="grid grid-cols-3 gap-4 mb-6">
          <UploadStatCard
            title="Festivals"
            imported={uploadStats.festivalsImported}
            skipped={uploadStats.festivalsSkipped}
          />
          <UploadStatCard
            title="Venues"
            imported={uploadStats.venuesImported}
            skipped={uploadStats.venuesSkipped}
          />
          <UploadStatCard
            title="Residencies"
            imported={uploadStats.residenciesImported}
            skipped={uploadStats.residenciesSkipped}
          />
        </div>

        {/* Errors */}
        {uploadStats.errors.length > 0 && (
          <div className="border-t pt-4">
            <p className="text-sm font-semibold text-red-600 dark:text-red-400 mb-3">
              Import Errors ({uploadStats.errors.length})
            </p>
            <div className="rounded p-3 space-y-1 max-h-48 overflow-y-auto">
              {uploadStats.errors.map((error, index) => (
                <p key={index} className="text-sm text-red-700 dark:text-red-300">
                  {error}
                </p>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
