-- Author Reveal.js Auto-Animate attributes with ordinary RST classes.
-- Classes on RST headings become attributes on the generated slide sections.
local function reveal_attributes(element)
  for _, class in ipairs(element.classes) do
    if class == 'auto-animate' then
      element.attributes['data-auto-animate'] = 'true'
      element.attributes['data-auto-animate-duration'] = '1.0'
      element.attributes['data-auto-animate-easing'] = 'ease-in-out'
    end
    local group = class:match('^animate%-group%-(.+)$')
    if group then
      element.attributes['data-auto-animate-id'] = group
    end
    local id = class:match('^animate%-id%-(.+)$')
    if id then
      element.attributes['data-id'] = id
    end
  end
  return element
end

return {{ Header = reveal_attributes, Div = reveal_attributes }}
