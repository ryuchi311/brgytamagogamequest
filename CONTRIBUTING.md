# Contributing to Telegram Bot Points System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Any relevant examples

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding style
   - Add tests if applicable
   - Update documentation

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```
   
   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description
   - Link related issues
   - Include screenshots if UI changes

## 📝 Coding Standards

### Python Code Style

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

Example:
```python
def calculate_user_points(user_id: str, task_id: str) -> int:
    """
    Calculate points earned by user for a task.
    
    Args:
        user_id: The user's unique identifier
        task_id: The task's unique identifier
    
    Returns:
        int: Points earned
    """
    # Implementation
    pass
```

### JavaScript Code Style

- Use ES6+ features
- Use const/let instead of var
- Write clear comments
- Follow consistent naming conventions

### HTML/CSS

- Use semantic HTML
- Keep CSS organized
- Make designs responsive
- Ensure accessibility

## 🧪 Testing

- Write tests for new features
- Ensure existing tests pass
- Test on multiple environments if possible

Run tests:
```bash
python test_setup.py
pytest
```

## 📚 Documentation

- Update README.md if needed
- Add inline comments for complex logic
- Update API documentation
- Include examples

## 🔒 Security

- Never commit sensitive data (API keys, passwords)
- Use environment variables
- Follow security best practices
- Report security issues privately

## 📋 Checklist Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No sensitive data in commits
- [ ] Changes are tested locally

## 🌟 Recognition

Contributors will be acknowledged in:
- README.md Contributors section
- Release notes
- Project website (if applicable)

## 📞 Questions?

If you have questions, feel free to:
- Open an issue
- Start a discussion
- Contact maintainers

Thank you for contributing! 🎉
