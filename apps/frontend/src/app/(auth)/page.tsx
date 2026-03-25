"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { CalendarCheck, Building2, Globe, Send, Star, BarChart3, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import LoginForm from "@/components/page-components/auth/components/LoginForm";
const features = [
  {
    icon: CalendarCheck,
    title: "Festival Tracking",
    description:
      "Discover and track festivals worldwide. Never miss a deadline or opportunity again.",
  },
  {
    icon: Building2,
    title: "Residency Management",
    description:
      "Browse artist residencies, manage your applications, and keep all details in one place.",
  },
  {
    icon: Globe,
    title: "Venue Discovery",
    description:
      "Find performance venues that match your art form, capacity needs, and location preferences.",
  },
  {
    icon: Send,
    title: "Application Tracking",
    description:
      "Track every application from draft to acceptance. Stay organized across all your submissions.",
  },
  {
    icon: Star,
    title: "Watchlists & Tags",
    description:
      "Star, watch, and tag opportunities to build a personalized pipeline of prospects.",
  },
  {
    icon: BarChart3,
    title: "Career Overview",
    description:
      "Get a bird's-eye view of your performing arts career with dashboards and insights.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="fixed top-0 z-50 w-full border-b bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <Image src="/logo.png" width={36} height={36} alt="Clapp logo" />
            <span className="font-clapp text-2xl text-primary">Clapp</span>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild>
              <Link href="/login">Log in</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Get started</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative flex min-h-screen items-center justify-center overflow-hidden pt-16">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
        <div className="relative mx-auto max-w-6xl px-6 text-center">
          <div className="flex justify-center gap-8 mb-16">
            <h1 className="font-clapp text-8xl text-primary self-center">Clapp</h1>
            <Image src={"/logo.png"} width={150} height={150} alt="Clapp logo" />
          </div>
          <h1 className="mx-auto max-w-4xl text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
            Your freelance arts career,{" "}
            <span className="text-primary">all in one place</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
            Track festivals, residencies, venues, and applications. Clapp is your personal assistant
            for managing every step of your career as a freelance artist.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" className="text-base px-8" asChild>
              <Link href="/register">
                Start for free <ArrowRight className="ml-1 size-5" />
              </Link>
            </Button>
            <Button size="lg" variant="tertiary" className="text-base px-8" asChild>
              <a href="#login">Log in to your account</a>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-primary">
              Everything you need
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              Manage your career with confidence
            </h2>
            <p className="mt-4 text-muted-foreground">
              From discovering opportunities to tracking applications, Clapp gives freelance artists
              the tools to stay organized and focused.
            </p>
          </div>
          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <Card
                key={feature.title}
                className="border-transparent bg-muted/40 transition-colors hover:border-primary/30 hover:bg-muted/60"
              >
                <CardContent className="pt-6">
                  <div className="mb-4 flex size-12 items-center justify-center rounded-lg bg-primary/10">
                    <feature.icon className="size-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold">{feature.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Login Section */}
      <section id="login" className="py-24 sm:py-32">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mx-auto grid max-w-5xl items-center gap-12 lg:grid-cols-2">
            <div>
              <p className="text-sm font-semibold uppercase tracking-widest text-primary">
                Welcome back
              </p>
              <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
                Ready to pick up where you left off?
              </h2>
              <p className="mt-4 text-muted-foreground">
                Log in to access your dashboard, review upcoming deadlines, and manage your
                applications.
              </p>
              <Separator className="my-8" />
              <p className="text-sm text-muted-foreground">
                Don&apos;t have an account yet?{" "}
                <Link
                  href="/register"
                  className="font-medium text-primary underline-offset-4 hover:underline"
                >
                  Create one for free
                </Link>
              </p>
            </div>
            <div>
              <LoginForm />
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 sm:flex-row">
          <div className="flex items-center gap-2">
            <Image src="/logo.png" width={24} height={24} alt="Clapp logo" />
            <span className="font-clapp text-lg text-primary">Clapp</span>
          </div>
          <p className="text-sm text-muted-foreground">Built for artists, by artists.</p>
        </div>
      </footer>
    </div>
  );
}
