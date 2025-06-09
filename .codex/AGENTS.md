# Global Development Guidelines

## Personal Development Preferences

### Code Quality Standards
- **Type Safety First**: Always use static typing (TypeScript for JS, type hints for Python, interfaces for Go)
- **Error Handling**: Never use bare `try/except` or ignore errors - always handle explicitly
- **Immutability**: Prefer immutable data structures and functional programming patterns
- **Documentation**: Every public function/method must have comprehensive docstrings
- **Testing**: Minimum 80% code coverage, with 100% for critical financial logic

### Security Best Practices
- **Never Commit Secrets**: Use `.env.example` files with placeholder values
- **Secrets Management**: Always use proper secret management tools (Vault, SOPS, etc.)
- **Input Validation**: Validate and sanitize all external inputs
- **Audit Trail**: Log all significant operations with correlation IDs
- **Principle of Least Privilege**: Grant minimal necessary permissions

### Development Workflow
- **Branch Strategy**: Use GitFlow - feature branches from `develop`, merge to `main` for releases
- **Commit Messages**: Use conventional commits format: `type(scope): description`
- **Pre-commit Hooks**: Always run linting, formatting, and basic tests before commit
- **Code Reviews**: No direct pushes to main/develop - all changes via PR

### Tool Preferences
- **Linting**: Use industry-standard linters (eslint, pylint, golangci-lint)
- **Formatting**: Auto-format with prettier/black/gofmt - no manual formatting
- **Testing**: Prefer testing frameworks with good mocking capabilities
- **Dependencies**: Pin exact versions in production, use lock files
- **Containers**: Use multi-stage builds for optimized production images

## Communication Style
- **PR Titles**: Use conventional commit format with scope
- **Commit Messages**: Include issue numbers and clear context
- **Code Comments**: Explain "why" not "what" - focus on business logic
- **Documentation**: Use markdown with clear examples and API contracts

## Quality Gates
- All code must pass linting without warnings
- Tests must pass with no skipped tests
- Security scans must show no high/critical vulnerabilities
- Performance regressions require explicit approval
- Breaking changes require version bump and migration guide
