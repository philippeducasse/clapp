"use client";

import { useEffect } from "react";
import { useSelector } from "react-redux";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppDispatch } from "@/redux/hook";
import { fetchFestivals, selectAllFestivals } from "@/redux/slices/festivalSlice";
import { fetchApplications, selectAllApplications } from "@/redux/slices/applicationSlice";
import { fetchVenues, selectAllVenues } from "@/redux/slices/venueSlice";
import { fetchResidencies, selectAllResidencies } from "@/redux/slices/residencySlice";
import { selectProfile } from "@/redux/slices/authSlice";
import DashboardCard, {
  DashboardCardProps,
} from "@/components/page-components/dashboard/components/DashboardCard";
import ApplicationStats from "@/components/page-components/dashboard/components/ApplicationStats";
import ProfileCompletionCard from "@/components/page-components/dashboard/components/ProfileCompletionCard";

const Page = () => {
  const dispatch = useAppDispatch();
  const festivals = useSelector(selectAllFestivals);
  const applications = useSelector(selectAllApplications);
  const venues = useSelector(selectAllVenues);
  const residencies = useSelector(selectAllResidencies);
  const profile = useSelector(selectProfile);

  useEffect(() => {
    if (festivals.length === 0) {
      dispatch(fetchFestivals());
    }
    if (applications.length === 0) {
      dispatch(fetchApplications());
    }
    if (venues.length === 0) {
      dispatch(fetchVenues());
    }
    if (residencies.length === 0) {
      dispatch(fetchResidencies());
    }
  }, [dispatch, festivals.length, applications.length, venues.length, residencies.length]);

  const overviewCardData: DashboardCardProps[] = [
    { title: "Total Applications", value: applications.length, subtitle: "All submissions" },
    { title: "Total Festivals", value: festivals.length },
    { title: "Total Venues", value: venues.length },
    { title: "Total Residencies", value: residencies.length },
  ];

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-semibold text-emerald-600 dark:text-emerald-400">
            Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            Welcome back! Here&apos;s your performance career overview.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {overviewCardData.map((data, index) => (
          <DashboardCard
            title={data.title}
            value={data.value}
            subtitle={data.subtitle}
            key={`${data.title}_${index}`}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Takes 2/3 */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">
                Application Breakdown
              </CardTitle>
              <CardDescription className="text-xl">
                Detailed status of all your applications
              </CardDescription>
            </CardHeader>
            <CardContent>
              {applications.length === 0 ? (
                <div className="text-muted-foreground text-sm">No applications yet</div>
              ) : (
                <ApplicationStats applications={applications} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">
                Profile Completion
              </CardTitle>
              <CardDescription className="text-xl">
                Complete your profile to improve application success
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!profile ? (
                <div className="text-muted-foreground text-sm">Loading profile...</div>
              ) : (
                <ProfileCompletionCard profile={profile} />
              )}
            </CardContent>
          </Card>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">
              Upcoming Deadlines
            </CardTitle>
            <CardDescription className="text-xl">
              Application deadlines and important dates
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center align-middle my-auto">
            <div className="text-muted-foreground text-3xl">Feature coming soon!</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Page;
