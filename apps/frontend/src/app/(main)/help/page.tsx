import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BookOpen,
  Building2,
  FileText,
  Mail,
  CheckCircle2,
  ArrowRight,
  Users,
  Zap,
  Settings,
  BarChart3,
} from "lucide-react";

export default function GettingStartedPage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="mb-12 flex justify-between items-start gap-6">
        <div>
          <h1 className="text-4xl font-bold text-emerald-700 mb-3">Getting Started Guide</h1>
          <p className="text-lg text-gray-600">
            Welcome to Circus Agent Frontend! This guide will walk you through the key features and
            help you get the most out of the platform.
          </p>
        </div>

        {/* Quick Links Box */}
        <Card className="flex-shrink-0 w-full sm:w-72 h-fit">
          <CardHeader>
            <CardTitle className="text-base">Quick Links</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Link
                href="/help/email-settings"
                className="block p-3 rounded-lg border border-gray-200 hover:border-emerald-400 hover:bg-emerald-50 transition text-sm font-medium text-gray-900 hover:text-emerald-700"
              >
                Email Settings Guide
              </Link>
              <Link
                href="/help/importing-organizations"
                className="block p-3 rounded-lg border border-gray-200 hover:border-emerald-400 hover:bg-emerald-50 transition text-sm font-medium text-gray-900 hover:text-emerald-700"
              >
                Importing Organizations
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Overview */}
      <Card className="mb-8 border-l-4 border-l-emerald-500 bg-emerald-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-emerald-600" />
            What is Circus Agent?
          </CardTitle>
        </CardHeader>
        <CardContent className="text-gray-700 space-y-3">
          <p>
            Circus Agent is your personal assistant for managing your performance arts career. It
            helps you:
          </p>
          <ul className="space-y-2 ml-4">
            <li className="flex items-start gap-3">
              <span className="text-emerald-600 font-bold">•</span>
              <span>Find and organize festivals, venues, and residency opportunities</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-600 font-bold">•</span>
              <span>Submit applications directly from the platform</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-600 font-bold">•</span>
              <span>Track your applications and deadlines in one place</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-emerald-600 font-bold">•</span>
              <span>Manage your professional profile and applications</span>
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Core Features */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-emerald-700 mb-6">Core Features</h2>
        <div className="space-y-6">
          {/* Feature 1: Storing Organizations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-blue-600" />
                Store & Organize Performance Opportunities
              </CardTitle>
              <CardDescription>Manage festivals, venues, and residencies</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-700">
                Build your own database of performance opportunities. Every festival, venue, and
                residency you add is saved to your account, making it easy to track and revisit
                opportunities.
              </p>
              <div className="bg-blue-50 p-4 rounded-lg space-y-3">
                <h4 className="font-semibold text-blue-900">You can:</h4>
                <ul className="text-sm text-blue-800 space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Create new festivals, venues, or residencies manually</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Import organizations from Excel files</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Add contact information for each organization</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Star or watch opportunities for quick access</span>
                  </li>
                </ul>
              </div>
              <p className="text-sm text-gray-600">
                Navigate to <strong>Festivals</strong>, <strong>Venues</strong>, or{" "}
                <strong>Residencies</strong> in the sidebar to start building your database.
              </p>
            </CardContent>
          </Card>

          {/* Feature 2: Viewing & Editing */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-purple-600" />
                View & Edit Organization Details
              </CardTitle>
              <CardDescription>Keep information up-to-date and organized</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-700">
                Once you&apos;ve added an organization, you can view all its details and make
                updates anytime. This ensures you always have the most current contact information
                and opportunity details.
              </p>
              <div className="bg-purple-50 p-4 rounded-lg space-y-3">
                <h4 className="font-semibold text-purple-900">You can:</h4>
                <ul className="text-sm text-purple-800 space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>View complete organization profiles</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Edit names, contact details, and key information</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Manage multiple contacts per organization</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Tag organizations to keep track of statuses</span>
                  </li>
                </ul>
              </div>
              <p className="text-sm text-gray-600">
                Click on any festival, venue, or residency in the table to view its full details and
                access the edit option.
              </p>
            </CardContent>
          </Card>

          {/* Feature 3: Applying */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-green-600" />
                Submit Applications Directly
              </CardTitle>
              <CardDescription>Apply to opportunities without leaving the platform</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-700">
                Submit applications to festivals, venues, and residencies directly through the
                platform. Your email will be configured to send from your own account, so
                you&apos;ll appear in their inbox personally.
              </p>
              <div className="bg-green-50 p-4 rounded-lg space-y-3">
                <h4 className="font-semibold text-green-900">You can:</h4>
                <ul className="text-sm text-green-800 space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Apply directly from the organization&apos;s detail page</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Customize your application message</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Include your performance materials and CV</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Send applications using your own email account</span>
                  </li>
                </ul>
              </div>
              <p className="text-sm text-gray-600">
                To apply, you&apos;ll need to <strong>configure your email settings first</strong>.
                See the &quot;Profile Setup&quot; section below.
              </p>
            </CardContent>
          </Card>

          {/* Feature 4: Tracking */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-orange-600" />
                Track Application Progress
              </CardTitle>
              <CardDescription>Never miss a deadline or lose track of submissions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-700">
                Keep all your applications in one place and track their status at a glance. See
                which opportunities you&apos;ve applied to, when, and what the status is.
              </p>
              <div className="bg-orange-50 p-4 rounded-lg space-y-3">
                <h4 className="font-semibold text-orange-900">You can:</h4>
                <ul className="text-sm text-orange-800 space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>View all your applications in one dashboard</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>Filter applications by status (submitted, accepted, rejected, etc.)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>View application deadlines and submission dates</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>See statistics on your application success rate</span>
                  </li>
                </ul>
              </div>
              <p className="text-sm text-gray-600">
                Go to <strong>Applications</strong> in the sidebar to see your application dashboard
                and full history.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Profile Setup - Most Important */}
      <Card className="mb-8 border-l-4 border-l-red-500 bg-red-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-red-600" />
            Complete Your Profile (Essential!)
          </CardTitle>
          <CardDescription className="text-red-800">
            This is the most important step to start applying
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-700 font-semibold">
            Before you can submit applications, you need to set up your profile. This includes:
          </p>

          <div className="space-y-4">
            {/* Step 1: Basic Profile */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center font-semibold">
                1
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2">Basic Profile Information</h4>
                <p className="text-gray-700 text-sm mb-3">
                  Your name, location, bio, and professional details. This information is important
                  for organizations to learn about you.
                </p>
                <Button asChild variant="outline" size="sm">
                  <Link href="/profile/">Go to Profile Settings</Link>
                </Button>
              </div>
            </div>

            {/* Step 2: Email Configuration */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center font-semibold">
                2
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2">Configure Email Settings</h4>
                <p className="text-gray-700 text-sm mb-3">
                  <strong>This is required to send applications.</strong> You&apos;ll set up your
                  email account so that when you apply through Circus Agent, organizations receive
                  emails from your personal email address. This is a one-time setup.
                </p>
                <div className="space-y-2 space-x-2">
                  <Button asChild size="sm">
                    <Link href="/profile/edit/email-settings" className="flex items-center gap-2">
                      Set Up Email <ArrowRight className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button asChild variant="outline" size="sm">
                    <Link href="/help/email-settings">View Email Setup Guide</Link>
                  </Button>
                </div>
              </div>
            </div>

            {/* Step 3: Performance Materials */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center font-semibold">
                3
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2">Add Performance Materials</h4>
                <p className="text-gray-700 text-sm mb-3">
                  Upload videos, images, and documents that showcase your work. These can be
                  attached to your applications to help organizations learn more about you.
                </p>
                <Button asChild variant="outline" size="sm">
                  <Link href="profile#performances">Go to Performances</Link>
                </Button>
              </div>
            </div>
          </div>

          <div className="bg-red-100 border border-red-300 rounded-lg p-4 mt-4">
            <p className="text-sm text-red-900">
              <strong>💡 Pro tip:</strong> Start with email setup and basic profile information to
              get started applying. You can add performance materials later.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Quick Start Flow */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-emerald-600" />
            Quick Start Flow
          </CardTitle>
          <CardDescription>Get your first application sent in 5 steps</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold text-sm">
                1
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900">Complete Basic Profile</p>
                <p className="text-sm text-gray-600">
                  Visit Profile settings and add your name, bio, and location
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold text-sm">
                2
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900">Set Up Email</p>
                <p className="text-sm text-gray-600">
                  Configure your email account in Email Settings
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold text-sm">
                3
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900">Add or Find Organizations</p>
                <p className="text-sm text-gray-600">
                  Create a festival/venue or import them from Excel
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold text-sm">
                4
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900">Submit Your First Application</p>
                <p className="text-sm text-gray-600">
                  Click &apos;Apply&apos; on any opportunity and submit
                </p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-semibold text-sm">
                5
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900">Track Your Application</p>
                <p className="text-sm text-gray-600">View it in the Applications dashboard</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Help Topics */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Help Topics</CardTitle>
          <CardDescription>Dive deeper into specific features</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <Link href="/help/email-settings" className="group">
              <div className="p-4 rounded-lg border border-gray-200 hover:border-emerald-400 hover:bg-emerald-50 transition">
                <div className="flex items-start gap-3">
                  <Mail className="h-5 w-5 text-emerald-600 mt-1 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-gray-900 group-hover:text-emerald-700">
                      Email Settings Configuration
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Detailed guide to setting up your email for sending applications
                    </p>
                  </div>
                </div>
              </div>
            </Link>

            {/* More help topics can be added here as they&apos;re created */}
            <div className="p-4 rounded-lg border border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed">
              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-gray-400 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-600">Importing Organizations</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Coming soon: Bulk import from Excel files
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg border border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed">
              <div className="flex items-start gap-3">
                <BarChart3 className="h-5 w-5 text-gray-400 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-600">Tracking Applications</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    Coming soon: Using the applications dashboard
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg border border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed">
              <div className="flex items-start gap-3">
                <Users className="h-5 w-5 text-gray-400 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-gray-600">Managing Your Profile</h4>
                  <p className="text-sm text-gray-500 mt-1">Coming soon: Profile best practices</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* CTA */}
      <Card className="border-l-4 border-l-emerald-500 bg-emerald-50">
        <CardHeader>
          <CardTitle>Ready to Get Started?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-700">
            Start with your profile setup, then browse and apply to opportunities. You&apos;ll be
            submitting applications in no time!
          </p>
          <div className="flex flex-col sm:flex-row gap-3">
            <Button asChild className="bg-emerald-600 hover:bg-emerald-700">
              <Link href="/profile/edit">Complete Your Profile</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/festivals">Browse Festivals</Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Bug Report Footer */}
      <div className="mt-12 pt-8 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-600 mb-3">Found an issue or have feedback?</p>
        <Button asChild variant="outline" size="sm">
          <Link href="/report-bug">Report a Bug</Link>
        </Button>
      </div>
    </div>
  );
}
