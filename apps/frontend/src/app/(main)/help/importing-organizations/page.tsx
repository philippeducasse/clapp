/* eslint-disable react/no-unescaped-entities */
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, CheckCircle2, AlertCircle, Download, FileText } from "lucide-react";

export default function ImportingOrganizationsHelpPage() {
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

        <Card>
          <CardHeader>
            <CardTitle>Excel File Format</CardTitle>
            <CardDescription>
              Your Excel file must have these columns (order doesn't matter)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="overflow-x-auto">
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="border border-gray-300 px-4 py-2 text-left font-semibold">
                      Column
                    </th>
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
                      Organization's website URL
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
                    Country, Website, Date, Email, Contact, Comments. The columns can be in any
                    order. You can have empty cells for optional fields.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Step-by-Step Import Guide</CardTitle>
            <CardDescription>Follow these steps to import your organizations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold">
                  1
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">Prepare Your Excel File</h3>
                  <p className="text-gray-600 mb-3">
                    Create an Excel file (.xlsx or .xls) with your organization data. Make sure you
                    follow the format exactly:
                  </p>
                  <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside ml-2">
                    <li>
                      First row contains the column headers (Type, Name, Country, Website, Date,
                      Email, Contact, Comments)
                    </li>
                    <li>
                      Columns can be in any order - the system reads the headers to match columns
                    </li>
                    <li>Each subsequent row is one organization</li>
                    <li>For Type, use: "Festival", "Venue", or "Residency"</li>
                    <li>Leave cells empty if you don't have data for optional fields</li>
                  </ul>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold">
                    2
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">Go to Upload Page</h3>
                    <p className="text-gray-600 mb-3">
                      Navigate to the Upload page in your Clapp dashboard. You can find it in the
                      sidebar menu.
                    </p>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold">
                    3
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">Select Your File</h3>
                    <p className="text-gray-600">
                      Click the file upload area and select your Excel file. The system will
                      validate the file format before import.
                    </p>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold">
                    4
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">Submit and Review</h3>
                    <p className="text-gray-600 mb-3">
                      Click "Upload" to submit your file. The system will process the data and show
                      you a summary of what was imported.
                    </p>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold">
                    5
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">Check Results</h3>
                    <p className="text-gray-600">
                      You'll see a summary showing how many organizations were imported and if there
                      were any errors. Check your Festivals, Venues, or Residencies pages to see
                      your imported organizations.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

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
              <h4 className="font-semibold text-gray-900 mb-2">File Size Limit</h4>
              <p className="text-gray-600 text-sm">
                Excel files should be under 10MB. If your file is larger, split it into multiple
                files and upload them separately.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-orange-600" />
              Common Issues
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Card className="bg-orange-50 border-orange-200">
              <CardContent className="pt-4">
                <h4 className="font-semibold text-orange-900 mb-2">"Invalid Type" Error</h4>
                <p className="text-sm text-orange-800">
                  Make sure you're using exactly: "Festival", "Venue", or "Residency" (case
                  matters).
                </p>
              </CardContent>
            </Card>

            <Card className="bg-orange-50 border-orange-200">
              <CardContent className="pt-4">
                <h4 className="font-semibold text-orange-900 mb-2">Some rows were skipped</h4>
                <p className="text-sm text-orange-800">
                  This usually means required fields are missing. Check that Type, Name, and Country
                  are filled for every organization.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-orange-50 border-orange-200">
              <CardContent className="pt-4">
                <h4 className="font-semibold text-orange-900 mb-2">File format not recognized</h4>
                <p className="text-sm text-orange-800">
                  Save your file as Excel format (.xlsx or .xls), not as CSV or other formats.
                </p>
              </CardContent>
            </Card>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Example Excel File</CardTitle>
            <CardDescription>Here's what your Excel file should look like</CardDescription>
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
      </div>
    </div>
  );
}
