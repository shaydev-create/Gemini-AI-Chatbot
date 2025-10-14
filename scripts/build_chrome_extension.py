#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 CHROME WEB STORE PACKAGE BUILDER
=================================

Automated script to create a production-ready Chrome extension package
for Chrome Web Store submission.

Features:
- Validates all required files
- Optimizes images and code
- Creates submission-ready ZIP
- Generates validation report
"""

import json
import shutil
import zipfile
from pathlib import Path


class ChromeExtensionPackager:
    """Utility to package Chrome extension for Web Store submission."""

    def __init__(self, extension_dir: str, output_dir: str = None):
        self.extension_dir = Path(extension_dir)
        self.output_dir = Path(output_dir) if output_dir else Path("dist")
        self.validation_errors = []
        self.validation_warnings = []

    def validate_manifest(self) -> bool:
        """Validate manifest.json for Chrome Web Store compliance."""
        manifest_path = self.extension_dir / "manifest.json"

        if not manifest_path.exists():
            self.validation_errors.append("manifest.json not found")
            return False

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # Required fields
            required_fields = ["manifest_version", "name", "version", "description"]
            for field in required_fields:
                if field not in manifest:
                    self.validation_errors.append(f"Missing required field: {field}")

            # Manifest version check
            if manifest.get("manifest_version") != 3:
                self.validation_errors.append("Must use Manifest V3")

            # Description length check
            description = manifest.get("description", "")
            if len(description) > 132:
                self.validation_errors.append(
                    f"Description too long: {len(description)}/132 characters"
                )

            # Icons check
            if "icons" not in manifest:
                self.validation_warnings.append("No icons specified")
            else:
                required_sizes = ["16", "48", "128"]
                for size in required_sizes:
                    if size not in manifest["icons"]:
                        self.validation_warnings.append(f"Missing {size}x{size} icon")

            return len(self.validation_errors) == 0

        except json.JSONDecodeError:
            self.validation_errors.append("Invalid JSON in manifest.json")
            return False

    def validate_icons(self) -> bool:
        """Validate required icon files exist."""
        icons_dir = self.extension_dir / "icons"
        required_icons = ["icon_16.png", "icon_48.png", "icon_128.png"]

        missing_icons = []
        for icon in required_icons:
            icon_path = icons_dir / icon
            if not icon_path.exists():
                missing_icons.append(icon)

        if missing_icons:
            self.validation_errors.extend(
                [f"Missing icon: {icon}" for icon in missing_icons]
            )
            return False

        return True

    def validate_privacy_policy(self) -> bool:
        """Validate privacy policy file exists and is accessible."""
        privacy_files = ["privacy_policy_en.html", "privacy_policy.html"]

        for privacy_file in privacy_files:
            privacy_path = self.extension_dir / privacy_file
            if privacy_path.exists():
                return True

        self.validation_warnings.append("No privacy policy file found")
        return False

    def validate_required_files(self) -> bool:
        """Validate all required files exist."""
        required_files = [
            "manifest.json",
            "popup.html",
            "popup.css",
            "popup.js",
            "background.js",
        ]

        missing_files = []
        for file in required_files:
            file_path = self.extension_dir / file
            if not file_path.exists():
                missing_files.append(file)

        if missing_files:
            self.validation_errors.extend(
                [f"Missing required file: {file}" for file in missing_files]
            )
            return False

        return True

    def optimize_files(self, temp_dir: Path):
        """Optimize files for production."""
        print("🔧 Optimizing files for production...")

        # Copy all files to temp directory first
        shutil.copytree(self.extension_dir, temp_dir, dirs_exist_ok=True)

        # Remove development files
        dev_files = [
            "SCREENSHOTS_GUIDE.md",
            "CHROME_STORE_DESCRIPTION.md",
            "SUBMISSION_CHECKLIST.md",
            ".gitignore",
            "README.md",
        ]

        for dev_file in dev_files:
            dev_path = temp_dir / dev_file
            if dev_path.exists():
                if dev_path.is_file():
                    dev_path.unlink()
                else:
                    shutil.rmtree(dev_path)

        # Minify CSS and JS files (basic minification)
        self._minify_css_files(temp_dir)
        self._minify_js_files(temp_dir)

        print("✅ File optimization complete")

    def _minify_css_files(self, directory: Path):
        """Basic CSS minification."""
        for css_file in directory.glob("**/*.css"):
            try:
                content = css_file.read_text(encoding="utf-8")
                # Basic minification: remove comments and extra whitespace
                import re

                content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
                content = re.sub(r"\s+", " ", content)
                content = content.replace("; ", ";").replace(": ", ":")
                css_file.write_text(content, encoding="utf-8")
            except Exception as e:
                print(f"⚠️ Could not minify {css_file}: {e}")

    def _minify_js_files(self, directory: Path):
        """Basic JS minification."""
        for js_file in directory.glob("**/*.js"):
            try:
                content = js_file.read_text(encoding="utf-8")
                # Basic minification: remove comments and extra whitespace
                import re

                content = re.sub(r"//.*?\n", "\n", content)
                content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
                content = re.sub(r"\s+", " ", content)
                js_file.write_text(content, encoding="utf-8")
            except Exception as e:
                print(f"⚠️ Could not minify {js_file}: {e}")

    def create_zip_package(self, temp_dir: Path) -> Path:
        """Create ZIP package for Chrome Web Store."""
        zip_name = "gemini-ai-chatbot-chrome-extension.zip"
        zip_path = self.output_dir / zip_name

        print(f"📦 Creating ZIP package: {zip_path}")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)

        print(f"✅ Package created: {zip_path}")
        print(f"📏 Package size: {zip_path.stat().st_size / 1024:.1f} KB")

        return zip_path

    def generate_validation_report(self) -> str:
        """Generate validation report."""
        report = []
        report.append("🔍 CHROME WEB STORE VALIDATION REPORT")
        report.append("=" * 50)

        if self.validation_errors:
            report.append(f"\n❌ ERRORS ({len(self.validation_errors)}):")
            for error in self.validation_errors:
                report.append(f"  • {error}")
        else:
            report.append("\n✅ NO CRITICAL ERRORS FOUND")

        if self.validation_warnings:
            report.append(f"\n⚠️ WARNINGS ({len(self.validation_warnings)}):")
            for warning in self.validation_warnings:
                report.append(f"  • {warning}")
        else:
            report.append("\n✅ NO WARNINGS")

        # Overall status
        if not self.validation_errors:
            report.append("\n🎯 STATUS: READY FOR SUBMISSION ✅")
        else:
            report.append("\n🎯 STATUS: REQUIRES FIXES BEFORE SUBMISSION ❌")

        return "\n".join(report)

    def build_package(self) -> bool:
        """Main method to build the Chrome Web Store package."""
        print("🚀 Starting Chrome Web Store package build...")

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Validation phase
        print("\n📋 Validating extension...")

        self.validate_manifest()
        self.validate_icons()
        self.validate_required_files()
        self.validate_privacy_policy()

        # Generate validation report
        report = self.generate_validation_report()
        print(f"\n{report}")

        # Stop if critical errors
        if self.validation_errors:
            print("\n❌ Build failed due to validation errors")
            return False

        # Create temporary directory for optimized files
        temp_dir = self.output_dir / "temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        try:
            # Optimize files
            self.optimize_files(temp_dir)

            # Create ZIP package
            zip_path = self.create_zip_package(temp_dir)

            # Save validation report
            report_path = self.output_dir / "validation_report.txt"
            report_path.write_text(report, encoding="utf-8")

            print("\n🎉 Build completed successfully!")
            print(f"📦 Package: {zip_path}")
            print(f"📋 Report: {report_path}")

            return True

        finally:
            # Cleanup temporary directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    extension_dir = project_root / "chrome_extension"
    output_dir = project_root / "dist"

    packager = ChromeExtensionPackager(str(extension_dir), str(output_dir))
    success = packager.build_package()

    if success:
        print("\n✅ Ready for Chrome Web Store submission!")
        print("\nNext steps:")
        print("1. 📸 Create screenshots for store listing")
        print("2. 🏪 Setup Chrome Web Store developer account")
        print("3. 📤 Upload ZIP file to Chrome Web Store")
        print("4. 📝 Complete store listing with descriptions")
        print("5. 🚀 Submit for review")
    else:
        print("\n❌ Build failed. Please fix validation errors and try again.")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
