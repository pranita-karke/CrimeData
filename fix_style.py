
import os

style_path = r'd:\CrimeData\static\css\style.css'

new_css = """
/* Header Navigation - Bold White Style */
.nav-menu {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.nav-item {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 600;
    cursor: pointer;
    font-size: 1rem;
    padding: 0.5rem 0;
    position: relative;
    transition: color 0.2s, opacity 0.2s;
    text-transform: capitalize;
}

.nav-item:hover,
.nav-item.active {
    color: #ffffff;
    opacity: 1;
}

.nav-item.active::after {
    content: '';
    position: absolute;
    bottom: -22px; /* Adjust based on header height */
    left: 0;
    width: 100%;
    height: 3px;
    background: #ffffff;
    border-radius: 3px 3px 0 0;
}

/* User Info & Logout */
.user-info {
    margin-left: 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.user-name {
    font-size: 0.95rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
}

.nav-logout {
    color: #ffffff;
    font-weight: 700;
    text-decoration: none;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    opacity: 0.9;
    transition: opacity 0.2s;
}

.nav-logout:hover {
    opacity: 1;
    text-decoration: underline;
}
"""

with open(style_path, 'rb') as f:
    content = f.read()

# Find the end of the slideUp keyframe
# We look for the last closing brace of the keyframe before the garbage starts
marker = b'@keyframes slideUp'
idx = content.find(marker)

if idx != -1:
    # Find the closing brace of the keyframe block
    # It contains "to { ... }" so two closing braces 
    # Let's search for "transform: translateY(0);\r\n        opacity: 1;\r\n    }\r\n}" or similar
    # Easier: just truncate at byte 8609 if we knew the offset, but dynamic is better.
    # The view_file output showed garbage starting at line 362: "}/ *   H e..."
    
    # We will look for the text right before the garbage
    end_marker = b'opacity: 1;\r\n    }\r\n}'
    # Try different line endings
    if end_marker not in content:
        end_marker = b'opacity: 1;\n    }\n}'
    
    end_idx = content.find(end_marker)
    
    if end_idx != -1:
        # Keep everything up to the end of the marker
        valid_content = content[:end_idx + len(end_marker)]
        
        # Write back
        with open(style_path, 'wb') as f:
            f.write(valid_content)
            f.write(b'\n\n')
            f.write(new_css.encode('utf-8'))
        print("Successfully cleaned and appended CSS.")
    else:
        print("Could not find end marker. Appending anyway.")
        # If we can't find marker, we might just append and hope strict CSS parsers ignore garbage
        with open(style_path, 'wb') as f:
            f.write(content)
            f.write(new_css.encode('utf-8'))
else:
    print("Could not find keyframes slideUp.")

