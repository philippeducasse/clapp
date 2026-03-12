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

interface OAuthEmailSectionProps {
  profile: Profile;
}

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

  const isOAuthActive = profile.oauthProvider !== null;

  return (
    <Card className="mb-6">
      <CardContent>
        <div className="flex items-center gap-2 mb-6">
          <Mail className="text-emerald-600 dark:text-emerald-400" size={20} />
          <CardTitle className="text-lg font-semibold">
            Email Configuration
          </CardTitle>
        </div>

        <div className="space-y-4">
          <div className="flex gap-3 pb-4 border-b">
            <Button
              onClick={() => handleConnect("gmail")}
              disabled={isLoading}
              variant={profile.oauthProvider === "GMAIL" ? "default" : "outline"}
              size="sm"
            >
              {profile.oauthProvider === "GMAIL" ? "✓ Gmail Connected" : "Connect Gmail"}
            </Button>
            <Button
              onClick={() => handleConnect("outlook")}
              disabled={isLoading}
              variant={profile.oauthProvider === "OUTLOOK" ? "default" : "outline"}
              size="sm"
            >
              {profile.oauthProvider === "OUTLOOK" ? "✓ Outlook Connected" : "Connect Outlook"}
            </Button>
            {isOAuthActive && (
              <Button
                onClick={handleDisconnect}
                disabled={isLoading}
                variant="destructive"
                size="sm"
              >
                Disconnect
              </Button>
            )}
          </div>

          <div className={isOAuthActive ? "opacity-50" : ""}>
            <div className="flex items-center gap-2 mb-3">
              <Lock size={16} className="text-gray-400" />
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Manual Configuration
              </p>
            </div>
            <div className="space-y-2 ml-6">
              {getEmailSettings(profile).map((setting, idx) => {
                let displayValue = "—";
                if (typeof setting.value === "boolean") {
                  displayValue = setting.value ? "Yes" : "No";
                } else if (setting.value instanceof Date) {
                  displayValue = setting.value.toString();
                } else if (setting.value) {
                  displayValue = String(setting.value);
                }
                return (
                  <div key={idx} className="text-sm">
                    <span className="font-medium">{setting.title}:</span>{" "}
                    <span className="text-gray-600 dark:text-gray-400">{displayValue}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default OAuthEmailSection;