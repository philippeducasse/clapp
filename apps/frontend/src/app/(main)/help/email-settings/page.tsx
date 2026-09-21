/* eslint-disable react/no-unescaped-entities */
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  AlertCircle,
  CheckCircle2,
  ExternalLink,
  Lock,
  Mail,
  Settings,
  Shield,
  AlertTriangle,
} from "lucide-react";

export default function EmailSettingsHelpPage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-primary mb-2 mt-4">
          Email Settings Configuration Guide
        </h1>
        <p className="text-gray-600 text-lg">
          Complete guide to configuring your email account for sending applications
        </p>
      </div>

      <div className="space-y-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5 text-blue-600" />
              Why Configure Email Settings?
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-700">
            <p>
              This application sends emails on your behalf when you submit applications to cultural
              organisations. By configuring your email account, you ensure that recipients see
              emails coming from your own email address.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-primary" />
              What You'll Need
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-semibold">Email Address</p>
                  <p className="text-sm text-gray-600">
                    The email you want to send applications from.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-semibold">Password</p>
                  <p className="text-sm text-gray-600">
                    A special password for third-party applications for most providers. For some,
                    this is the same as the one you use to log into your email.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-semibold">SMTP Port</p>
                  <p className="text-sm text-gray-600">
                    Usually 587. Changing the port might result in your emails not being sent or
                    having a higher likelihood of going straight to spam.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-semibold">Email Provider</p>
                  <p className="text-sm text-gray-600">
                    We'll automatically configure major email providers (Gmail, Outlook, etc.). For
                    other providers, enter your SMTP host (e.g., ssl0.ovh.net for OVH). Check your
                    provider's documentation if unsure.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="h-5 w-5 text-primary" />
              Understanding App Passwords
            </CardTitle>
            <CardDescription>
              When you need them and how they keep your account secure
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-700">
              Many modern email providers require <strong>app passwords</strong> instead of your
              regular email password for security reasons. An app password is a unique,
              automatically-generated password that gives specific applications access to your email
              account without exposing your main password.
            </p>

            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="">
                <div className="flex gap-3">
                  <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-blue-900">Do I Need an App Password?</p>
                    <p className="text-sm text-blue-800 mt-1">
                      Most providers require app passwords. See the categories below to check if
                      yours does.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid md:grid-cols-3 gap-4">
              <Card className="border-primary/30 bg-primary/5">
                <CardContent className="">
                  <h4 className="font-semibold text-primary text-sm mb-2">Always Required</h4>
                  <p className="text-xs text-primary/80 mb-2">
                    These providers always require app passwords for security:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {["Gmail", "AOL", "Fastmail", "ProtonMail", "Mail.ru", "T-Online"].map(
                      (provider) => (
                        <Badge key={provider} variant="outline" className="text-xs">
                          {provider}
                        </Badge>
                      ),
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-yellow-200 bg-yellow-50">
                <CardContent className="">
                  <h4 className="font-semibold text-yellow-900 text-sm mb-2">Required with 2FA</h4>
                  <p className="text-xs text-yellow-800 mb-2">
                    Only needed if you have two-factor authentication enabled:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {["Outlook", "Yahoo", "iCloud", "Zoho", "GMX", "Web.de", "Virgilio"].map(
                      (provider) => (
                        <Badge key={provider} variant="outline" className="text-xs">
                          {provider}
                        </Badge>
                      ),
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-gray-200 bg-gray-50">
                <CardContent className="">
                  <h4 className="font-semibold text-gray-900 text-sm mb-2">Regular Password OK</h4>
                  <p className="text-xs text-gray-800 mb-2">
                    You can use your regular email password:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {["Orange", "Free", "Libero"].map((provider) => (
                      <Badge key={provider} variant="outline" className="text-xs">
                        {provider}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="bg-yellow-50 border-yellow-500">
              <CardContent className="">
                <div className="flex gap-3">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-yellow-900">Security Best Practice</p>
                    <p className="text-sm text-yellow-800 mt-1">
                      Even if your provider doesn't require an app password, using one (if
                      available) is more secure than using your regular password. This way, if this
                      app is compromised, your main email password stays safe.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Step-by-Step Setup Guide</CardTitle>
            <CardDescription>Follow these steps to configure your email settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                  1
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">Select Your Email Provider</h3>
                  <p className="text-gray-600">
                    Choose your email provider from the dropdown list. The form will automatically
                    update to show provider-specific instructions and settings.
                  </p>
                </div>
              </div>

              <Separator />

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                  2
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">Generate an App Password</h3>
                  <p className="text-gray-600 mb-3">
                    Click the "Detailed instructions" link in the password field to visit your
                    provider's documentation. Follow their guide to generate an app password.
                  </p>
                  <Card className="bg-gray-50">
                    <CardContent className="pt-4">
                      <p className="text-sm font-semibold text-gray-700 mb-2">
                        Common steps include:
                      </p>
                      <ol className="text-sm text-gray-600 space-y-1 list-decimal list-inside">
                        <li>Enable two-factor authentication (if required)</li>
                        <li>Navigate to account security settings</li>
                        <li>Find "App Passwords" or similar option</li>
                        <li>Generate a new password for "Mail" or "SMTP"</li>
                        <li>Copy the generated password</li>
                      </ol>
                    </CardContent>
                  </Card>
                </div>
              </div>

              <Separator />

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                  3
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">Enter Your Credentials</h3>
                  <p className="text-gray-600 mb-3">Fill in the form fields:</p>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span className="text-gray-700">
                        <strong>Email:</strong> Your full email address
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span className="text-gray-700">
                        <strong>Password:</strong> Paste the app password you generated (not your
                        regular password)
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span className="text-gray-700">
                        <strong>Port:</strong> Pre-filled based on your provider (usually 587)
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span className="text-gray-700">
                        <strong>TLS:</strong> Pre-configured based on your provider's requirements
                      </span>
                    </li>
                  </ul>
                </div>
              </div>

              <Separator />

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                  4
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">Save and Test</h3>
                  <p className="text-gray-600">
                    Click "Save" to store your email settings. The system will validate your
                    credentials. If successful, you're ready to send applications!
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div>
          <h2 className="text-2xl font-bold text-primary mb-4">Provider-Specific Notes</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  Gmail
                  <Badge variant="secondary">Port 587</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>
                  Gmail requires 2-Step Verification to be enabled before you can create app
                  passwords.
                </p>
                <Button variant="outline" size="sm" asChild className="w-full">
                  <a
                    href="https://support.google.com/mail/answer/185833"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    View Gmail Setup Guide
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  Outlook/Hotmail
                  <Badge variant="secondary">Port 587</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>
                  Microsoft deprecated basic authentication in September 2025. App passwords now
                  required.
                </p>
                <Button variant="outline" size="sm" asChild className="w-full">
                  <a
                    href="https://support.microsoft.com/en-us/account-billing/manage-app-passwords-for-two-step-verification-d6dc8c6d-4bf7-4851-ad95-6d07799387e9"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    View Outlook Setup Guide
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  ProtonMail
                  <Badge variant="secondary">Port 1025</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>
                  Requires ProtonMail Bridge desktop application. Bridge must be running locally.
                </p>
                <Button variant="outline" size="sm" asChild className="w-full">
                  <a
                    href="https://proton.me/support/protonmail-bridge-install"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    Download Bridge & Setup Guide
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  iCloud Mail
                  <Badge variant="secondary">Port 587</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>
                  Requires app-specific password for all third-party apps. Go to appleid.apple.com
                  to generate.
                </p>
                <Button variant="outline" size="sm" asChild className="w-full">
                  <a
                    href="https://support.apple.com/en-us/102654"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    View iCloud Setup Guide
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  Yahoo Mail
                  <Badge variant="secondary">Port 587</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>
                  App passwords required when using third-party apps. Generate in Account Security
                  settings.
                </p>
                <Button variant="outline" size="sm" asChild className="w-full">
                  <a
                    href="https://help.yahoo.com/kb/SLN15241.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    View Yahoo Setup Guide
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  T-Online
                  <Badge variant="secondary">Port 587</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>
                  Requires separate E-Mail-Password that's different from main account password.
                </p>
                <Button variant="outline" size="sm" asChild className="w-full">
                  <a
                    href="https://www.telekom.de/hilfe/festnetz-internet-tv/e-mail/e-mail-adresse-einrichten"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    View T-Online Setup Guide
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              Troubleshooting Common Issues
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Card className="bg-red-50 border-red-200">
              <CardContent className="pt-4">
                <h3 className="font-semibold text-red-900 mb-2">"Authentication Failed" Error</h3>
                <ul className="text-sm text-red-800 space-y-1">
                  <li>• Double-check you're using the app password, not your regular password</li>
                  <li>• Ensure there are no extra spaces when copying the password</li>
                  <li>• Verify that 2-Step Verification is enabled (if required)</li>
                  <li>• Try regenerating a new app password</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-red-50 border-red-200">
              <CardContent className="pt-4">
                <h3 className="font-semibold text-red-900 mb-2">"Connection Failed" Error</h3>
                <ul className="text-sm text-red-800 space-y-1">
                  <li>• Check that the port number is correct (usually 587)</li>
                  <li>• Ensure TLS is enabled for your provider</li>
                  <li>• Verify your firewall isn't blocking SMTP connections</li>
                  <li>• For ProtonMail: Make sure Bridge is running on your computer</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-red-50 border-red-200">
              <CardContent className="pt-4">
                <h3 className="font-semibold text-red-900 mb-2">
                  "App Passwords Not Available" Error
                </h3>
                <ul className="text-sm text-red-800 space-y-1">
                  <li>• Enable 2-Step Verification first</li>
                  <li>• Some providers require you to wait 24-48 hours after enabling 2FA</li>
                  <li>
                    • For Fastmail: Ensure you're not on a Basic plan (app passwords not available)
                  </li>
                </ul>
              </CardContent>
            </Card>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Security Best Practices
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              <li className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Never share your app passwords</strong>
                  <p className="text-sm text-gray-600">Treat them like regular passwords</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Revoke unused passwords</strong>
                  <p className="text-sm text-gray-600">
                    If you stop using this app, revoke the app password from your email provider's
                    settings
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Use unique passwords</strong>
                  <p className="text-sm text-gray-600">
                    Don't reuse the same app password across multiple applications
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Monitor account activity</strong>
                  <p className="text-sm text-gray-600">
                    Regularly check your email account's recent activity for any suspicious behavior
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <strong>Keep 2FA enabled</strong>
                  <p className="text-sm text-gray-600">
                    Two-factor authentication adds an extra layer of security to your account
                  </p>
                </div>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-primary bg-primary/5">
          <CardHeader>
            <CardTitle>Need More Help?</CardTitle>
            <CardDescription className="text-primary/80">
              If you're still having trouble configuring your email settings, each provider has
              detailed documentation available through the "Detailed instructions" links in the
              form.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full md:w-auto">
              <Link href="/profile/edit/email-settings">Go to Email Settings Form</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
