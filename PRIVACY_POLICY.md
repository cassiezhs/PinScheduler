# Privacy Policy

Last updated: June 14, 2026

## Overview

Pinflow Automation is a folder-based tool that publishes prepared content to Pinterest. This privacy policy explains what information the application processes and how that information is handled.

## Information Processed

Pinflow Automation may process:

- Pinterest access tokens provided through environment variables or GitHub repository secrets
- Post metadata, including titles, descriptions, links, alt text, board IDs, image URLs, schedules, and status values
- Pinterest API responses, including Pinterest pin IDs and response statuses
- Operational logs, including successful post records and error messages

## How Information Is Used

Information is used only to:

- Authenticate requests to the Pinterest API
- Publish scheduled Pinterest pins
- Track successful publishing activity
- Diagnose publishing errors
- Prevent duplicate posts

## Storage and Security

Pinterest access tokens are not intentionally written to application logs or committed to the repository. Tokens should be stored in a local `.env` file or GitHub repository secrets.

Post metadata and operational logs are stored locally in the project folders or in the associated GitHub repository. Repository owners are responsible for controlling access to these files and removing sensitive information before committing changes.

## Third-Party Services

Pinflow Automation sends publishing requests and post information to Pinterest through Pinterest API v5. Pinterest processes this information according to its own privacy policy and developer terms.

Image URLs and destination links may be hosted by third parties. Those services may collect information according to their own privacy policies.

## Data Retention

Published post folders and publishing logs are retained until the repository owner deletes them. Failed post folders and error logs are also retained until manually removed.

## Data Sharing

Pinflow Automation does not sell personal information. Information is shared only with services required to publish content, such as Pinterest and any third-party image or link hosting providers selected by the repository owner.

## Children's Privacy

Pinflow Automation is not designed to collect personal information from children.

## Changes to This Policy

This privacy policy may be updated as the application changes. Updates will be reflected by changing the "Last updated" date.

## Contact

For privacy questions, contact the project owner at:

`YOUR_CONTACT_EMAIL`
