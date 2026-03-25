"use client";

import { useState } from "react";
import { Mail, Lock } from "lucide-react";
import { Card, CardContent, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Profile } from "@/interfaces/entities/Profile";
import { oauthEmailService } from "@/api/oauthEmailService";
import { useDispatch } from "react-redux";
import { profileApiService } from "@/api/profileApiService";
import { updateProfile } from "@/redux/slices/authSlice";
import { getEmailSettings } from "../helpers/getEmailSettings";
import { capitalizeFirst } from "@/utils/stringUtils";

interface OAuthEmailSectionProps {
  profile: Profile;
}

const GmailIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="mr-2">
    <path
      d="M20.4 4H3.6C2.16 4 1.2 4.96 1.2 6.4v11.2c0 1.44.96 2.4 2.4 2.4h16.8c1.44 0 2.4-.96 2.4-2.4V6.4c0-1.44-.96-2.4-2.4-2.4zm0 3.6l-8.4 5.28L3.6 7.6v-1.2l8.4 5.28 8.4-5.28v1.2z"
      fill="#EA4335"
    />
  </svg>
);

const OutlookIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="mr-2">
    <path d="M2 4h7v7H2V4zm0 9h7v7H2v-7zm9-9h7v7h-7V4zm0 9h7v7h-7v-7z" fill="#0078D4" />
  </svg>
);

const OAuthEmailSection = ({ profile }: OAuthEmailSectionProps) => {
  const dispatch = useDispatch();
  const [isLoading, setIsLoading] = useState(false);

  const handleConnect = async (provider: "gmail" | "outlook") => {
    try {
      setIsLoading(true);
      if (provider === "gmail") {
        await oauthEmailService.connectGmail();
      } else {
        await oauthEmailService.connectOutlook();
      }
    } catch (error) {
      console.error(`Failed to connect ${provider}:`, error);
      setIsLoading(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      setIsLoading(true);
      await oauthEmailService.disconnect();
      const updatedProfile = await profileApiService.get();
      dispatch(updateProfile(updatedProfile));
    } catch (error) {
      console.error("Failed to disconnect:", error);
    } finally {
      setIsLoading(false);
    }
  };
  console.log("porifle", profile);

  return (
    <Card className="mb-6">
      <CardContent>
        <div className="flex items-center gap-2 mb-6">
          <Mail className="text-primary" size={20} />
          <CardTitle className="text-lg font-semibold">Click to connect</CardTitle>
        </div>
        <p className="font-light text-gray-600 dark:text-foreground mb-8">
          Connect your Gmail or Outlook mailbox with just a few clicks using the buttons below.{" "}
          <br></br> If you use an other provider, you will need to manually setup up the connection.
        </p>

        <div className="flex gap-4">
          <Button
            onClick={() => handleConnect("gmail")}
            disabled={isLoading}
            variant={profile.oauthProvider === "GMAIL" ? "tertiary" : "outline"}
          >
            <GmailIcon />
            {profile.oauthProvider === "GMAIL" ? "✓ Gmail Connected" : "Connect Gmail"}
          </Button>
          <Button
            onClick={() => handleConnect("outlook")}
            disabled={isLoading}
            variant={profile.oauthProvider === "OUTLOOK" ? "tertiary" : "outline"}
          >
            <OutlookIcon />
            {profile.oauthProvider === "OUTLOOK" ? "✓ Outlook Connected" : "Connect Outlook"}
          </Button>
          {profile.oauthProvider && (
            <Button onClick={handleDisconnect} disabled={isLoading} variant="destructive">
              {`Disconnect ${capitalizeFirst(profile.oauthProvider)}`}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default OAuthEmailSection;
