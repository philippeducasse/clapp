import React from "react";
import { Profile } from "@/interfaces/entities/Profile";
import { Progress } from "@/components/ui/progress";

const ProfileCompletionCard = ({ profile }: { profile: Profile }) => {
  const calculateProfileCompletion = () => {
    if (!profile) return { percentage: 0, completed: 0, total: 0, missingFields: [] };

    const fields = [
      { name: "Account confirmed", value: profile.confirmedAccount },
      { name: "First Name", value: profile.firstName },
      { name: "Last Name", value: profile.lastName },
      { name: "Company Name", value: profile.companyName },
      { name: "Personal Website", value: profile.personalWebsite },
      { name: "Location", value: profile.location },
      { name: "Nationality", value: profile.nationality },
      {
        name: "Spoken Languages",
        value: profile.spokenLanguages && profile.spokenLanguages.length > 0,
      },
      { name: "Instagram Profile", value: profile.instagramProfile },
      { name: "Facebook Profile", value: profile.facebookProfile },
      { name: "TikTok Profile", value: profile.tiktokProfile },
      { name: "YouTube Profile", value: profile.youtubeProfile },
      { name: "Performances", value: profile.performances && profile.performances.length > 0 },
      { name: "Email Configuration", value: profile.emailHost && profile.emailHostUser },
    ];

    const completed = fields.filter((field) => field.value).length;
    const total = fields.length;
    const percentage = Math.round((completed / total) * 100);
    const missingFields = fields.filter((field) => !field.value).map((field) => field.name);

    return { percentage, completed, total, missingFields };
  };

  const profileCompletion = calculateProfileCompletion();

  return (
    <>
      <div className="flex items-center justify-between">
        <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
          {profileCompletion.percentage}%
        </span>
        <span className="text-sm text-muted-foreground">
          {profileCompletion.completed} of {profileCompletion.total} fields completed
        </span>
      </div>
      <Progress value={profileCompletion.percentage} className="h-2" color="emerald-600" />
      {profileCompletion.missingFields.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium">Missing fields:</p>
          <ul className="text-sm text-muted-foreground space-y-1">
            {profileCompletion.missingFields.slice(0, 5).map((field) => (
              <li key={field} className="flex items-center gap-2">
                <span className="size-1.5 rounded-full bg-muted-foreground" />
                {field}
              </li>
            ))}
            {profileCompletion.missingFields.length > 5 && (
              <li className="text-xs italic">
                +{profileCompletion.missingFields.length - 5} more fields
              </li>
            )}
          </ul>
        </div>
      )}
    </>
  );
};

export default ProfileCompletionCard;
