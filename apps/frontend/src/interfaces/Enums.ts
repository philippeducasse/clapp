export enum Action {
  CREATE = "CREATE",
  EDIT = "EDIT",
  APPLY = "APPLY",
  REGISTER = "REGISTER",
  LOGIN = "LOGIN",
  UPLOAD = "UPLOAD",
  REPORT_BUG = "REPORT_BUG",
}

export enum EntityName {
  FESTIVAL = "FESTIVAL",
  APPLICATION = "APPLICATION",
  RESIDENCY = "RESIDENCY",
  VENUE = "VENUE",
  PROFILE = "PROFILE",
  PERFORMANCE = "PERFORMANCE",
  EMAIL_TEMPLATE = "EMAIL_TEMPLATE",
  PREFERENCES = "PREFERENCES",
}

export enum TagAction {
  STAR = "STAR",
  WATCH = "WATCH",
  INACTIVE = "INACTIVE",
  WARNING = "WARNING",
  IRRELEVANT = "IRRELEVANT",
  OTHER = "OTHER",
}

export enum OrganisationType {
  FESTIVAL = "FESTIVAL",
  VENUE = "VENUE",
  RESIDENCY = "RESIDENCY",
}

export enum EmailHost {
  GMAIL = "GMAIL",
  OUTLOOK = "OUTLOOK",
  YAHOO = "YAHOO",
  ICLOUD = "ICLOUD",
  PROTONMAIL = "PROTONMAIL",
  ZOHO = "ZOHO",
  AOL = "AOL",
  FASTMAIL = "FASTMAIL",
  GMX = "GMX",
  WEB_DE = "WEB.DE",
  ORANGE = "ORANGE",
  FREE = "FREE",
  LIBERO = "LIBERO",
  MAIL_RU = "MAIL.RU",
  VIRGILIO = "VIRGILIO",
  T_ONLINE = "T-ONLINE",
  OTHER = "OTHER",
}

export interface EmailHostConfig {
  requiresAppPassword: boolean;
  helpText: string;
  smtpPort: number;
  useTls: boolean;
  documentationUrl?: string;
}

export const EMAIL_HOST_CONFIG: Record<EmailHost, EmailHostConfig> = {
  [EmailHost.GMAIL]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Gmail requires an app-specific password. Go to your Google Account Security settings, enable 2-Step Verification if not already enabled, then generate an App Password under 'App passwords'. Use that password here, not your regular Gmail password.",
    documentationUrl: "https://support.google.com/mail/answer/185833",
  },
  [EmailHost.OUTLOOK]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Outlook/Hotmail requires an app password if you have 2-Step Verification enabled. Go to your Microsoft account Security settings and create an app password. Note: Basic authentication was deprecated in September 2025.",
    documentationUrl:
      "https://support.microsoft.com/en-us/account-billing/manage-app-passwords-for-two-step-verification-d6dc8c6d-4bf7-4851-ad95-6d07799387e9",
  },
  [EmailHost.YAHOO]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Yahoo requires an app password when using third-party apps. Go to your Yahoo Account Security settings and generate an app password under 'Generate app password'. Use that password here instead of your regular Yahoo password.",
    documentationUrl: "https://help.yahoo.com/kb/SLN15241.html",
  },
  [EmailHost.ICLOUD]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "iCloud Mail requires an app-specific password. Go to appleid.apple.com, sign in, navigate to Security > App-Specific Passwords, and generate a new password. Use that password here, not your Apple ID password.",
    documentationUrl: "https://support.apple.com/en-us/102654",
  },
  [EmailHost.PROTONMAIL]: {
    requiresAppPassword: true,
    smtpPort: 1025,
    useTls: false,
    helpText:
      "ProtonMail requires Proton Mail Bridge for SMTP access. Download and install the Bridge application, then use the bridge-generated password here. Standard ProtonMail passwords will not work for SMTP. Note: Port 1025 is used via the local Bridge application.",
    documentationUrl: "https://proton.me/support/protonmail-bridge-install",
  },
  [EmailHost.ZOHO]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Zoho requires an app-specific password if you have Two-Factor Authentication enabled. Go to Zoho Account Security settings and generate an application-specific password. If 2FA is disabled, you can use your regular password.",
    documentationUrl: "https://www.zoho.com/mail/help/adminconsole/two-factor-authentication.html",
  },
  [EmailHost.AOL]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "AOL requires an app password for third-party applications. Go to your AOL Account Security settings, click 'Generate app password', and create a password specifically for this application.",
    documentationUrl: "https://help.aol.com/articles/Create-and-manage-app-password",
  },
  [EmailHost.FASTMAIL]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Fastmail requires an app password for SMTP access (not available on Basic plans). Go to Settings > Password & Security > App Passwords and create a new app password specifically for sending email.",
    documentationUrl: "https://www.fastmail.help/hc/en-us/articles/360058752854-App-passwords",
  },
  [EmailHost.GMX]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "GMX requires an app-specific password when two-factor authentication is enabled. Enable POP3/IMAP sync in your GMX settings, then generate an application-specific password in your security settings. If 2FA is disabled, use your regular password.",
    documentationUrl: "https://support.gmx.com/security/2fa/application-specific-passwords.html",
  },
  [EmailHost.WEB_DE]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Web.de requires an app-specific password when two-factor authentication is enabled. Go to your Web.de security settings and create an app password. If 2FA is disabled, you can use your regular password.",
    documentationUrl: "https://hilfe.web.de/sicherheit/two-factor-auth.html",
  },
  [EmailHost.ORANGE]: {
    requiresAppPassword: false,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Orange supports standard password authentication. Use your regular Orange email account password here.",
    documentationUrl: "https://assistance.orange.fr/",
  },
  [EmailHost.FREE]: {
    requiresAppPassword: false,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Free.fr uses authenticated SMTP. Use your regular Free email account password here. Make sure authenticated SMTP is activated in your Free account settings.",
    documentationUrl: "https://subscribe.free.fr/acces/acces_smtp.html",
  },
  [EmailHost.LIBERO]: {
    requiresAppPassword: false,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Libero.it supports OAuth2 or standard password authentication. You can use your regular Libero email password here.",
    documentationUrl: "https://aiuto.libero.it/",
  },
  [EmailHost.MAIL_RU]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Mail.ru requires an app password for external applications. Go to Mail ID settings > Security > Passwords for External Applications, click 'Add', and generate a password specifically for this application.",
    documentationUrl: "https://help.mail.ru/mail/security/protection/external",
  },
  [EmailHost.VIRGILIO]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Virgilio requires an app-specific password if you have Password Sicura (2FA) enabled. Generate an app password in your Virgilio account settings. If 2FA is disabled, you can use your regular password.",
    documentationUrl: "https://aiuto.virgilio.it/",
  },
  [EmailHost.T_ONLINE]: {
    requiresAppPassword: true,
    smtpPort: 587,
    useTls: true,
    helpText:
      "T-Online requires a separate email password that is different from your webmail login password. You must set up an 'E-Mail-Password' in your T-Online account settings specifically for use with email clients.",
    documentationUrl:
      "https://www.telekom.de/hilfe/festnetz-internet-tv/e-mail/e-mail-adresse-einrichten",
  },
  [EmailHost.OTHER]: {
    requiresAppPassword: false,
    smtpPort: 587,
    useTls: true,
    helpText:
      "Enter the password for your email account. Check your email provider's documentation to see if they require an app-specific password or if your regular password works.",
  },
};
