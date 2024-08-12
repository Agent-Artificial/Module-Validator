import os
import base64
import subprocess

folder_path = f'modules/embedding'

file_data = [
    ('data_models.py', 'ZnJvbSBhYmMgaW1wb3J0IEFCQywgYWJzdHJhY3RtZXRob2QKZnJvbSBweWRhbnRpYyBpbXBvcnQgQmFzZU1vZGVsCmZyb20gdHlwaW5nIGltcG9ydCBPcHRpb25hbCwgQW55LCBMaXRlcmFsCmZyb20gc3Vic3RyYXRlaW50ZXJmYWNlLnV0aWxzIGltcG9ydCBzczU4CgpUT1BJQ1MgPSBbCiAgICAiVGhlIHB1cnN1aXQgb2Yga25vd2xlZGdlIiwKICAgICJUaGUgaW1wYWN0IG9mIHRlY2hub2xvZ3kgb24gc29jaWV0eSIsCiAgICAiVGhlIHN0cnVnZ2xlIGJldHdlZW4gdHJhZGl0aW9uIGFuZCBtb2Rlcm5pdHkiLAogICAgIlRoZSBuYXR1cmUgb2YgZ29vZCBhbmQgZXZpbCIsCiAgICAiVGhlIGNvbnNlcXVlbmNlcyBvZiB3YXIiLAogICAgIlRoZSBzZWFyY2ggZm9yIGlkZW50aXR5IiwKICAgICJUaGUgam91cm5leSBvZiBzZWxmLWRpc2NvdmVyeSIsCiAgICAiVGhlIGVmZmVjdHMgb2YgZ3JlZWQiLAogICAgIlRoZSBwb3dlciBvZiBsb3ZlIiwKICAgICJUaGUgaW5ldml0YWJpbGl0eSBvZiBjaGFuZ2UiLAogICAgIlRoZSBxdWVzdCBmb3IgcG93ZXIiLAogICAgIlRoZSBtZWFuaW5nIG9mIGZyZWVkb20iLAogICAgIlRoZSBpbXBhY3Qgb2YgY29sb25pemF0aW9uIiwKICAgICJUaGUgaWxsdXNpb24gb2YgY2hvaWNlIiwKICAgICJUaGUgaW5mbHVlbmNlIG9mIG1lZGlhIiwKICAgICJUaGUgcm9sZSBvZiBlZHVjYXRpb24iLAogICAgIlRoZSBlZmZlY3RzIG9mIGlzb2xhdGlvbiIsCiAgICAiVGhlIGJhdHRsZSBhZ2FpbnN0IGlubmVyIGRlbW9ucyIsCiAgICAiVGhlIGNvcnJ1cHRpb24gb2YgaW5ub2NlbmNlIiwKICAgICJUaGUgbG9zcyBvZiBjdWx0dXJlIiwKICAgICJUaGUgdmFsdWUgb2YgYXJ0IiwKICAgICJUaGUgY29tcGxleGl0aWVzIG9mIGxlYWRlcnNoaXAiLAogICAgIlRoZSBuYXR1cmUgb2Ygc2FjcmlmaWNlIiwKICAgICJUaGUgZGVjZXB0aW9uIG9mIGFwcGVhcmFuY2VzIiwKICAgICJUaGUgY29uc2VxdWVuY2VzIG9mIGVudmlyb25tZW50YWwgZGVncmFkYXRpb24iLAogICAgIlRoZSBjeWNsZSBvZiBsaWZlIGFuZCBkZWF0aCIsCiAgICAiVGhlIGltcGFjdCBvZiBnbG9iYWwgY2FwaXRhbGlzbSIsCiAgICAiVGhlIHN0cnVnZ2xlIGZvciBlcXVhbGl0eSIsCiAgICAiVGhlIGluZmx1ZW5jZSBvZiByZWxpZ2lvbiIsCiAgICAiVGhlIGV4cGxvcmF0aW9uIG9mIHNwYWNlIiwKICAgICJUaGUgZWZmZWN0cyBvZiBhZGRpY3Rpb24iLAogICAgIlRoZSBkYW5nZXJzIG9mIGFtYml0aW9uIiwKICAgICJUaGUgZHluYW1pY3Mgb2YgZmFtaWx5IiwKICAgICJUaGUgbmF0dXJlIG9mIHRydXRoIiwKICAgICJUaGUgY29uc2VxdWVuY2VzIG9mIHNjaWVudGlmaWMgZXhwbG9yYXRpb24iLAogICAgIlRoZSBpbGx1c2lvbiBvZiBoYXBwaW5lc3MiLAogICAgIlRoZSBwdXJzdWl0IG9mIGJlYXV0eSIsCiAgICAiVGhlIGltcGFjdCBvZiBpbW1pZ3JhdGlvbiIsCiAgICAiVGhlIGNsYXNoIG9mIGNpdmlsaXphdGlvbnMiLAogICAgIlRoZSBzdHJ1Z2dsZSBhZ2FpbnN0IG9wcHJlc3Npb24iLAogICAgIlRoZSBxdWVzdCBmb3IgZXRlcm5hbCBsaWZlIiwKICAgICJUaGUgbmF0dXJlIG9mIHRpbWUiLAogICAgIlRoZSByb2xlIG9mIGZhdGUgYW5kIGRlc3RpbnkiLAogICAgIlRoZSBpbXBhY3Qgb2YgY2xpbWF0ZSBjaGFuZ2UiLAogICAgIlRoZSBkeW5hbWljcyBvZiByZXZvbHV0aW9uIiwKICAgICJUaGUgY2hhbGxlbmdlIG9mIHN1c3RhaW5hYmlsaXR5IiwKICAgICJUaGUgY29uY2VwdCBvZiB1dG9waWEgYW5kIGR5c3RvcGlhIiwKICAgICJUaGUgbmF0dXJlIG9mIGp1c3RpY2UiLAogICAgIlRoZSByb2xlIG9mIG1lbnRvcnNoaXAiLAogICAgIlRoZSBwcmljZSBvZiBmYW1lIiwKICAgICJUaGUgaW1wYWN0IG9mIG5hdHVyYWwgZGlzYXN0ZXJzIiwKICAgICJUaGUgYm91bmRhcmllcyBvZiBodW1hbiBjYXBhYmlsaXR5IiwKICAgICJUaGUgbXlzdGVyeSBvZiB0aGUgdW5rbm93biIsCiAgICAiVGhlIGNvbnNlcXVlbmNlcyBvZiBkZW5pYWwiLAogICAgIlRoZSBpbXBhY3Qgb2YgdHJhdW1hIiwKICAgICJUaGUgZXhwbG9yYXRpb24gb2YgdGhlIHN1YmNvbnNjaW91cyIsCiAgICAiVGhlIHBhcmFkb3ggb2YgY2hvaWNlIiwKICAgICJUaGUgbGltaXRhdGlvbnMgb2YgbGFuZ3VhZ2UiLAogICAgIlRoZSBpbmZsdWVuY2Ugb2YgZ2VuZXRpY3MiLAogICAgIlRoZSBkeW5hbWljcyBvZiBwb3dlciBhbmQgY29udHJvbCIsCiAgICAiVGhlIG5hdHVyZSBvZiBjb3VyYWdlIiwKICAgICJUaGUgZXJvc2lvbiBvZiBwcml2YWN5IiwKICAgICJUaGUgaW1wYWN0IG9mIGFydGlmaWNpYWwgaW50ZWxsaWdlbmNlIiwKICAgICJUaGUgY29uY2VwdCBvZiB0aGUgbXVsdGl2ZXJzZSIsCiAgICAiVGhlIHN0cnVnZ2xlIGZvciByZXNvdXJjZSBjb250cm9sIiwKICAgICJUaGUgZWZmZWN0cyBvZiBnbG9iYWxpemF0aW9uIiwKICAgICJUaGUgZHluYW1pY3Mgb2Ygc29jaWFsIGNsYXNzIiwKICAgICJUaGUgY29uc2VxdWVuY2VzIG9mIHVuYnJpZGxlZCBjYXBpdGFsaXNtIiwKICAgICJUaGUgaWxsdXNpb24gb2Ygc2VjdXJpdHkiLAogICAgIlRoZSByb2xlIG9mIG1lbW9yeSIsCiAgICAiVGhlIGR5bmFtaWNzIG9mIGZvcmdpdmVuZXNzIiwKICAgICJUaGUgY2hhbGxlbmdlcyBvZiBkZW1vY3JhY3kiLAogICAgIlRoZSBteXN0ZXJ5IG9mIGNyZWF0aW9uIiwKICAgICJUaGUgY29uY2VwdCBvZiBpbmZpbml0eSIsCiAgICAiVGhlIG1lYW5pbmcgb2YgaG9tZSIsCiAgICAiVGhlIGltcGFjdCBvZiBwYW5kZW1pY3MiLAogICAgIlRoZSByb2xlIG9mIG15dGhvbG9neSIsCiAgICAiVGhlIGZlYXIgb2YgdGhlIHVua25vd24iLAogICAgIlRoZSBjaGFsbGVuZ2Ugb2YgZXRoaWNhbCBkZWNpc2lvbnMiLAogICAgIlRoZSBuYXR1cmUgb2YgaW5zcGlyYXRpb24iLAogICAgIlRoZSBkeW5hbWljcyBvZiBleGNsdXNpb24gYW5kIGluY2x1c2lvbiIsCiAgICAiVGhlIGNvbnNlcXVlbmNlcyBvZiBwcmVqdWRpY2UiLAogICAgIlRoZSBlZmZlY3RzIG9mIGZhbWUgYW5kIGFub255bWl0eSIsCiAgICAiVGhlIG5hdHVyZSBvZiB3aXNkb20iLAogICAgIlRoZSBkeW5hbWljcyBvZiB0cnVzdCBhbmQgYmV0cmF5YWwiLAogICAgIlRoZSBzdHJ1Z2dsZSBmb3IgcGVyc29uYWwgYXV0b25vbXkiLAogICAgIlRoZSBjb25jZXB0IG9mIHJlYmlydGgiLAogICAgIlRoZSBtZWFuaW5nIG9mIHNhY3JpZmljZSIsCiAgICAiVGhlIGltcGFjdCBvZiB0ZXJyb3Jpc20iLAogICAgIlRoZSBjaGFsbGVuZ2Ugb2YgbWVudGFsIGhlYWx0aCIsCiAgICAiVGhlIGV4cGxvcmF0aW9uIG9mIGFsdGVybmF0ZSByZWFsaXRpZXMiLAogICAgIlRoZSBpbGx1c2lvbiBvZiBjb250cm9sIiwKICAgICJUaGUgY29uc2VxdWVuY2VzIG9mIHRlY2hub2xvZ2ljYWwgc2luZ3VsYXJpdHkiLAogICAgIlRoZSByb2xlIG9mIGludHVpdGlvbiIsCiAgICAiVGhlIGR5bmFtaWNzIG9mIGFkYXB0YXRpb24iLAogICAgIlRoZSBjaGFsbGVuZ2Ugb2YgbW9yYWwgZGlsZW1tYXMiLAogICAgIlRoZSBjb25jZXB0IG9mIGxlZ2FjeSIsCiAgICAiVGhlIGltcGFjdCBvZiBnZW5ldGljIGVuZ2luZWVyaW5nIiwKICAgICJUaGUgcm9sZSBvZiBhcnQgaW4gc29jaWV0eSIsCiAgICAiVGhlIGVmZmVjdHMgb2YgY3VsdHVyYWwgYXNzaW1pbGF0aW9uIiwKXQoKY2xhc3MgU3M1OEtleShCYXNlTW9kZWwpOgogICAgc3M1OF9hZGRyZXNzOiBzdHIKICAgIAogICAgZGVmIF9faW5pdF9fKHNlbGYsIGFkZHJlc3M6IHN0cikgLT4gTm9uZToKICAgICAgICBzZWxmLmFkZHJlc3MgPSBzZWxmLmVuY29kZShhZGRyZXNzKQogICAgICAgIHN1cGVyKCkuX19pbml0X18oYWRkcmVzcz1zZWxmLmFkZHJlc3MpCiAgICAKICAgIGRlZiBlbmNvZGUoc2VsZiwgcHVibGljX2FkZHJlc3M6IHN0cikgLT4gc3RyOgogICAgICAgIGVuY29kZWRfYWRkcmVzcyA9IHNzNTguc3M1OF9lbmNvZGUocHVibGljX2FkZHJlc3MpCiAgICAgICAgcmV0dXJuIHNlbGYuX19zZXRhdHRyX18oInNzNThfYWRkcmVzcyIsIGVuY29kZWRfYWRkcmVzcykKCiAgICBkZWYgX19zdHJfXyhzZWxmKSAtPiBzdHI6CiAgICAgICAgcmV0dXJuIHN0cihzZWxmLmFkZHJlc3MpCiAgICAKICAgIGRlZiBfX3NldGF0dHJfXyhzZWxmLCBuYW1lOiBzdHIsIHZhbHVlOiBBbnkpIC0+IE5vbmU6CiAgICAgICAgaWYgbmFtZSA9PSAic3M1OF9hZGRyZXNzIjoKICAgICAgICAgICAgcmV0dXJuIHN1cGVyKCkuX19zZXRhdHRyX18obmFtZSwgdmFsdWUpCiAgICAgICAgcmV0dXJuIHN1cGVyKCkuX19zZXRhdHRyX18obmFtZSwgc2VsZi5lbmNvZGUodmFsdWUpKQoKICAgIGRlZiBfX2hhc2hfXyhzZWxmKSAtPiBpbnQ6CiAgICAgICAgcmV0dXJuIGhhc2goc2VsZi5hZGRyZXNzKQogICAgCgpjbGFzcyBNaW5lckNvbmZpZyhCYXNlTW9kZWwpOgogICAgbW9kdWxlX25hbWU6IE9wdGlvbmFsW3N0cl0gPSAiZW1iZWRkaW5nIgogICAga2V5X25hbWU6IE9wdGlvbmFsW3N0cl0gPSAiZWRlbl9taW5lcjEiCiAgICBrZXlfcGF0aF9uYW1lOiBPcHRpb25hbFtzdHJdID0gImVkZW5fbWluZXIxIgogICAgaG9zdDogT3B0aW9uYWxbc3RyXSA9ICIwLjAuMC4wIgogICAgcG9ydDogT3B0aW9uYWxbaW50XSA9IDU5NTkKCgpjbGFzcyBNb2R1bGVDb25maWcoQmFzZU1vZGVsKToKICAgIGRlZiBfX2luaXRfXyhzZWxmLCAqKmt3YXJncyk6CiAgICAgICAgc3VwZXIoKS5fX3NldGF0dHJfXygqKmt3YXJncykKICAgICAgICAKICAgIGRlZiBfX3NldGF0dHJfXyhzZWxmLCBuYW1lOiBzdHIsIHZhbHVlOiBBbnkpIC0+IE5vbmU6CiAgICAgICAgaWYgbmFtZSA9PSAia2V5IjoKICAgICAgICAgICAgcmV0dXJuIHN1cGVyKCkuX19zZXRhdHRyX18obmFtZSwgU3M1OEtleSh2YWx1ZSkpCiAgICAgICAgcmV0dXJuIHN1cGVyKCkuX19zZXRhdHRyX18obmFtZSwgdmFsdWUpCgoKY2xhc3MgQmFzZU1vZHVsZShCYXNlTW9kZWwsIEFCQyk6CiAgICBkZWYgX19pbml0X18oc2VsZiwgKiprd2FyZ3MpIC0+IE5vbmU6CiAgICAgICAgZGVmIHNldGF0dHIoc2VsZiwgbmFtZTogc3RyLCB2YWx1ZTogQW55KSAtPiBOb25lOgogICAgICAgICAgICBpZiBuYW1lID09ICJrZXkiOgogICAgICAgICAgICAgICAgcmV0dXJuIHN1cGVyKCkuX19zZXRhdHRyX18obmFtZSwgU3M1OEtleSh2YWx1ZSkpCiAgICAgICAgICAgIHJldHVybiBzdXBlcigpLl9fc2V0YXR0cl9fKG5hbWUsIHZhbHVlKQogICAgICAgIHN1cGVyKCkuX19pbml0X18oKiprd2FyZ3MpCiAgICAgICAgc2VsZi5fX3NldGF0dHJfXyA9IHNldGF0dHIKICAgICAgICAKICAgIEBhYnN0cmFjdG1ldGhvZAogICAgYXN5bmMgZGVmIHByb2Nlc3Moc2VsZiwgdXJsOiBzdHIpIC0+IEFueToKICAgICAgICAiIiJQcm9jZXNzIGEgcmVxdWVzdCBtYWRlIHRvIHRoZSBtb2R1bGUuIiIiCgoKY2xhc3MgVG9rZW5Vc2FnZShCYXNlTW9kZWwpOgogICAgIiIiVG9rZW4gdXNhZ2UgbW9kZWwiIiIKICAgIHRvdGFsX3Rva2VuczogaW50ID0gMAogICAgcHJvbXB0X3Rva2VuczogaW50ID0gMAogICAgcmVxdWVzdF90b2tlbnM6IGludCA9IDAKICAgIHJlc3BvbnNlX3Rva2VuczogaW50ID0gMAogICAgCmNsYXNzIE1lc3NhZ2UoQmFzZU1vZGVsKToKICAgIGNvbnRlbnQ6IHN0cgogICAgcm9sZTogTGl0ZXJhbFsidXNlciIsICJhc3Npc3RhbnQiLCAic3lzdGVtIl0K'),
    ('__init__.py', ''),
    ('embedding.py', 'aW1wb3J0IHRpa3Rva2VuCmZyb20gdGlrdG9rZW4gaW1wb3J0IEVuY29kaW5nCmZyb20gbnVtcHkgaW1wb3J0IGZsb2F0aW5nCmZyb20gbnVtcHkuX3R5cGluZyBpbXBvcnQgXzY0Qml0CmZyb20gdHlwaW5nIGltcG9ydCBBbnksIExpc3QKZnJvbSBweWRhbnRpYyBpbXBvcnQgRmllbGQKZnJvbSAuZGF0YV9tb2RlbHMgaW1wb3J0IFRva2VuVXNhZ2UsIEJhc2VNb2R1bGUKCgplbmNvZGluZyA9IHRpa3Rva2VuLmdldF9lbmNvZGluZwoKCmNsYXNzIEVtYmVkZGluZ01vZHVsZShCYXNlTW9kdWxlKToKICAgIHRva2VuX3VzYWdlOiBUb2tlblVzYWdlID0gRmllbGQoZGVmYXVsdD1Ub2tlblVzYWdlKQogICAgaGlzdG9yaWNhbF9saXN0OiBMaXN0W1Rva2VuVXNhZ2VdID0gRmllbGQoZGVmYXVsdD1saXN0KQogICAgZW1iZWRkaW5nX2Z1bmN0aW9uOiBFbmNvZGluZyA9IEZpZWxkKGRlZmF1bHQ9ZW5jb2RpbmcpCiAgICBfX3B5ZGFudGljX2ZpZWxkc19zZXRfXyA9IHsidG9rZW5fdXNhZ2UiLCAiaGlzdG9yaWNhbF9saXN0IiwgImVtYmVkZGluZ19mdW5jdGlvbiJ9CiAgICBfX3B5ZGFudGljX2V4dHJhX18gPSB7ImFsbG93X3BvcHVsYXRpb25fYnlfZmllbGRfbmFtZSI6IFRydWV9CgogICAgY2xhc3MgQ29uZmlnOgogICAgICAgIGFyYml0cmFyeV90eXBlc19hbGxvd2VkID0gVHJ1ZQogICAgICAgIF9fcHlkYW50aWNfZXh0cmFfXyA9IHsiYWxsb3dfcG9wdWxhdGlvbl9ieV9maWVsZF9uYW1lIjogVHJ1ZX0KCiAgICBkZWYgX19pbml0X18oc2VsZikgLT4gTm9uZToKICAgICAgICAiIiIKICAgICAgICBJbml0aWFsaXplcyB0aGUgVGlrVG9rZW5NYW5hZ2VyIG9iamVjdCB3aXRoIHRoZSBwcm92aWRlZCBrZXl3b3JkIGFyZ3VtZW50cy4KCiAgICAgICAgUGFyYW1ldGVyczoKICAgICAgICAgICAgKiprd2FyZ3MgKGRpY3QpOiBBIGRpY3Rpb25hcnkgb2Yga2V5d29yZCBhcmd1bWVudHMuCiAgICAgICAgICAgICAgICAtIHRvdGFsIChpbnQpOiBUaGUgdG90YWwgbnVtYmVyIG9mIHRva2Vucy4KICAgICAgICAgICAgICAgIC0gcmVzcG9uc2VfdG9rZW5zIChpbnQpOiBUaGUgbnVtYmVyIG9mIHJlc3BvbnNlIHRva2Vucy4KICAgICAgICAgICAgICAgIC0gcHJvbXB0X3Rva2VucyAoaW50KTogVGhlIG51bWJlciBvZiBwcm9tcHQgdG9rZW5zLgoKICAgICAgICBSZXR1cm5zOgogICAgICAgICAgICBOb25lCiAgICAgICAgIiIiCiAgICAgICAgc3VwZXIoKS5fX2luaXRfXygpCiAgICAgICAgc2VsZi50b2tlbl91c2FnZTogVG9rZW5Vc2FnZSA9IFRva2VuVXNhZ2UoKQogICAgICAgIHNlbGYuaGlzdG9yaWNhbF9saXN0OiBMaXN0W1Rva2VuVXNhZ2VdID0gW10KICAgICAgICBzZWxmLmVtYmVkZGluZ19mdW5jdGlvbjogRW5jb2RpbmcgPSBlbmNvZGluZygiY2wxMDBrX2Jhc2UiKQoKICAgIGRlZiByZW1vdmUoc2VsZiwgaW5kZXgpIC0+IFRva2VuVXNhZ2U6CiAgICAgICAgIiIiCiAgICAgICAgUmVtb3ZlIGFuIGVsZW1lbnQgZnJvbSB0aGUgaGlzdG9yaWNhbCBsaXN0IGF0IHRoZSBzcGVjaWZpZWQgaW5kZXguCgogICAgICAgIFBhcmFtZXRlcnM6CiAgICAgICAgICAgIGluZGV4IChpbnQpOiBUaGUgaW5kZXggb2YgdGhlIGVsZW1lbnQgdG8gcmVtb3ZlLgoKICAgICAgICBSZXR1cm5zOgogICAgICAgICAgICBzdHI6IEEgbWVzc2FnZSBpbmRpY2F0aW5nIHRoYXQgdGhlIGluZGV4IGhhcyBiZWVuIHJlbW92ZWQuCgogICAgICAgIFJhaXNlczoKICAgICAgICAgICAgSW5kZXhFcnJvcjogSWYgdGhlIGluZGV4IGlzIG91dCBvZiByYW5nZS4KCiAgICAgICAgU2lkZSBFZmZlY3RzOgogICAgICAgICAgICAtIFRoZSBlbGVtZW50IGF0IHRoZSBzcGVjaWZpZWQgaW5kZXggaXMgcmVtb3ZlZCBmcm9tIHRoZSBoaXN0b3JpY2FsIGxpc3QuCiAgICAgICAgICAgIC0gSWYgdGhlIGluZGV4IGlzIDAsIHRoZSBzZXNzaW9uX3RvdGFsLCBwcm9tcHRfdG9rZW5zLCByZXF1ZXN0X3Rva2VucywgcmVzcG9uc2VfdG9rZW5zLCBhbmQgaGlzdG9yaWNhbF9saXN0IGF0dHJpYnV0ZXMgYXJlIHJlc2V0IHRvIDAgb3IgYW4gZW1wdHkgbGlzdC4KICAgICAgICAiIiIKICAgICAgICBzZWxmLmhpc3RvcmljYWxfbGlzdC5yZW1vdmUoc2VsZi5oaXN0b3JpY2FsX2xpc3RbaW5kZXhdKQogICAgICAgIGlmIGluZGV4ID09IDA6CiAgICAgICAgICAgIHNlbGYudG9rZW5fdXNhZ2UudG90YWxfdG9rZW5zID0gMAogICAgICAgICAgICBzZWxmLnRva2VuX3VzYWdlLnByb21wdF90b2tlbnMgPSAwCiAgICAgICAgICAgIHNlbGYudG9rZW5fdXNhZ2UucmVxdWVzdF90b2tlbnMgPSAwCiAgICAgICAgICAgIHNlbGYudG9rZW5fdXNhZ2UucmVzcG9uc2VfdG9rZW5zID0gMAogICAgICAgICAgICBzZWxmLmhpc3RvcmljYWxfbGlzdC5hcHBlbmQoVG9rZW5Vc2FnZSgqKnNlbGYudG9rZW5fdXNhZ2UubW9kZWxfZHVtcCgpKSkKCiAgICAgICAgcmV0dXJuIHNlbGYudG9rZW5fdXNhZ2UKCiAgICBkZWYgdXBkYXRlKHNlbGYsIHJlcXVlc3Q6IGludCwgcmVzcG9uc2U6IGludCkgLT4gVG9rZW5Vc2FnZToKICAgICAgICAiIiIKICAgICAgICBVcGRhdGVzIHRoZSBzZXNzaW9uIHRvdGFsLCBwcm9tcHQgdG9rZW5zLCByZXF1ZXN0IHRva2VucywgYW5kIHJlc3BvbnNlIHRva2VucyB3aXRoIHRoZSBwcm92aWRlZCB2YWx1ZXMuCgogICAgICAgIFBhcmFtZXRlcnM6CiAgICAgICAgICAgIHRvdGFsIChpbnQpOiBUaGUgdG90YWwgbnVtYmVyIG9mIHRva2Vucy4KICAgICAgICAgICAgcmVxdWVzdCAoaW50KTogVGhlIG51bWJlciBvZiByZXF1ZXN0IHRva2Vucy4KICAgICAgICAgICAgcmVzcG9uc2UgKGludCk6IFRoZSBudW1iZXIgb2YgcmVzcG9uc2UgdG9rZW5zLgoKICAgICAgICBSZXR1cm5zOgogICAgICAgICAgICBzdHI6IEEgbWVzc2FnZSBpbmRpY2F0aW5nIHRoYXQgdGhlIHVwZGF0ZSB3YXMgc3VjY2Vzc2Z1bC4KICAgICAgICAiIiIKICAgICAgICBzZWxmLnRva2VuX3VzYWdlLnJlcXVlc3RfdG9rZW5zID0gcmVxdWVzdCBvciAwCiAgICAgICAgc2VsZi50b2tlbl91c2FnZS5yZXNwb25zZV90b2tlbnMgPSByZXNwb25zZSBvciAwCiAgICAgICAgc2VsZi50b2tlbl91c2FnZS5wcm9tcHRfdG9rZW5zID0gc2VsZi50b2tlbl91c2FnZS5yZXF1ZXN0X3Rva2VucyArIHNlbGYudG9rZW5fdXNhZ2UucmVzcG9uc2VfdG9rZW5zCiAgICAgICAgc2VsZi50b2tlbl91c2FnZS50b3RhbF90b2tlbnMgKz0gc2VsZi50b2tlbl91c2FnZS5wcm9tcHRfdG9rZW5zCiAgICAgICAgc2VsZi5oaXN0b3JpY2FsX2xpc3QuYXBwZW5kKFRva2VuVXNhZ2UoKipzZWxmLnRva2VuX3VzYWdlLm1vZGVsX2R1bXAoKSkpCiAgICAgICAgcmV0dXJuIHNlbGYudG9rZW5fdXNhZ2UKCiAgICBkZWYgY291bnRfdG9rZW5zKHNlbGYsIHN0cmluZzogc3RyLCBlbmNvZGluZ19uYW1lOiBzdHIgPSAiY2wxMDBrX2Jhc2UiKSAtPiBpbnQ6CiAgICAgICAgIiIiCiAgICAgICAgQ291bnRzIHRoZSBudW1iZXIgb2YgdG9rZW5zIGluIGEgZ2l2ZW4gc3RyaW5nIHVzaW5nIHRoZSBzcGVjaWZpZWQgZW5jb2RpbmcuCgogICAgICAgIFBhcmFtZXRlcnM6CiAgICAgICAgICAgIHN0cmluZyAoc3RyKTogVGhlIGlucHV0IHN0cmluZyB0byBjb3VudCB0aGUgdG9rZW5zIG9mLgogICAgICAgICAgICBlbmNvZGluZ19uYW1lIChzdHIsIG9wdGlvbmFsKTogVGhlIG5hbWUgb2YgdGhlIGVuY29kaW5nIHRvIHVzZS4gRGVmYXVsdHMgdG8gImNsMTAwa19iYXNlIi4KCiAgICAgICAgUmV0dXJuczoKICAgICAgICAgICAgaW50OiBUaGUgbnVtYmVyIG9mIHRva2VucyBpbiB0aGUgaW5wdXQgc3RyaW5nLgogICAgICAgICIiIgogICAgICAgIGVtYmVkZGluZ19hcnJheTogdGlrdG9rZW4uRW5jb2RpbmcgPSB0aWt0b2tlbi5nZXRfZW5jb2RpbmcoCiAgICAgICAgICAgIGVuY29kaW5nX25hbWU9ZW5jb2RpbmdfbmFtZQogICAgICAgICkKICAgICAgICByZXR1cm4gbGVuKGVtYmVkZGluZ19hcnJheS5lbmNvZGUodGV4dD1zdHJpbmcpKQoKICAgIGRlZiBjb3NpbmVfc2ltaWxhcml0eSgKICAgICAgICBzZWxmLCBlbWJlZGRpbmcxOiBMaXN0W2ludF0sIGVtYmVkZGluZzI6IExpc3RbaW50XQogICAgKSAtPiBmbG9hdGluZ1tfNjRCaXQgfCBBbnldOgogICAgICAgICIiIgogICAgICAgIENhbGN1bGF0ZXMgdGhlIGNvc2luZSBzaW1pbGFyaXR5IGJldHdlZW4gdHdvIGVtYmVkZGluZ3MuCgogICAgICAgIFBhcmFtZXRlcnM6CiAgICAgICAgICAgIGVtYmVkZGluZzEgKExpc3RbaW50XSk6IFRoZSBmaXJzdCBlbWJlZGRpbmcuCiAgICAgICAgICAgIGVtYmVkZGluZzIgKExpc3RbaW50XSk6IFRoZSBzZWNvbmQgZW1iZWRkaW5nLgoKICAgICAgICBSZXR1cm5zOgogICAgICAgICAgICBmbG9hdDogVGhlIGNvc2luZSBzaW1pbGFyaXR5IGJldHdlZW4gdGhlIHR3byBlbWJlZGRpbmdzLgogICAgICAgICIiIgogICAgICAgIGZyb20gc2NpcHkuc3BhdGlhbCBpbXBvcnQgZGlzdGFuY2UKICAgICAgICBpbXBvcnQgbnVtcHkgYXMgbnAKCiAgICAgICAgbnBfZW1iZWRkaW5nMSA9IG5wLmFycmF5KG9iamVjdD1lbWJlZGRpbmcxKQogICAgICAgIG5wX2VtYmVkZGluZzIgPSBucC5hcnJheShvYmplY3Q9ZW1iZWRkaW5nMikKICAgICAgICByZXR1cm4gMSAtIGRpc3RhbmNlLmNvc2luZSh1PW5wX2VtYmVkZGluZzEsIHY9bnBfZW1iZWRkaW5nMikKCiAgICBkZWYgcHJvY2VzcyhzZWxmLCBzdHJpbmc6IHN0cikgLT4gTGlzdFtpbnRdOgogICAgICAgIGVtYmVkZGluZyA9IHNlbGYuZW1iZWRkaW5nX2Z1bmN0aW9uLmVuY29kZSh0ZXh0PXN0cmluZykKICAgICAgICBzZWxmLnVwZGF0ZShyZXF1ZXN0PWxlbihlbWJlZGRpbmcpLCByZXNwb25zZT0wKQogICAgICAgIHJldHVybiBlbWJlZGRpbmcKICAgIAogICAgCmlmIF9fbmFtZV9fID09ICdfX21haW5fXyc6CiAgICBtb2R1bGUgPSBFbWJlZGRpbmdNb2R1bGUoKQogICAgcHJpbnQobW9kdWxlLnByb2Nlc3MoImhlbGxvIHdvcmxkIikp'),
    ('install_embedding.sh', 'IyEvYmluL2Jhc2gKCgpwaXAgaW5zdGFsbCB0aWt0b2tlbiBudW1weSBzY2lweQ=='),
    ('embedding_module.py', 'aW1wb3J0IHRpa3Rva2VuCmZyb20gdGlrdG9rZW4gaW1wb3J0IEVuY29kaW5nCmZyb20gbnVtcHkgaW1wb3J0IGZsb2F0aW5nCmZyb20gbnVtcHkuX3R5cGluZyBpbXBvcnQgXzY0Qml0CmZyb20gdHlwaW5nIGltcG9ydCBBbnksIExpc3QKZnJvbSBweWRhbnRpYyBpbXBvcnQgRmllbGQKZnJvbSAuZGF0YV9tb2RlbHMgaW1wb3J0IFRva2VuVXNhZ2UsIEJhc2VNb2R1bGUKCgplbmNvZGluZyA9IHRpa3Rva2VuLmdldF9lbmNvZGluZwoKCmNsYXNzIEVtYmVkZGluZ01vZHVsZShCYXNlTW9kdWxlKToKICAgIHRva2VuX3VzYWdlOiBUb2tlblVzYWdlID0gRmllbGQoZGVmYXVsdD1Ub2tlblVzYWdlKQogICAgaGlzdG9yaWNhbF9saXN0OiBMaXN0W1Rva2VuVXNhZ2VdID0gRmllbGQoZGVmYXVsdD1saXN0KQogICAgZW1iZWRkaW5nX2Z1bmN0aW9uOiBFbmNvZGluZyA9IEZpZWxkKGRlZmF1bHQ9ZW5jb2RpbmcpCiAgICBfX3B5ZGFudGljX2ZpZWxkc19zZXRfXyA9IHsidG9rZW5fdXNhZ2UiLCAiaGlzdG9yaWNhbF9saXN0IiwgImVtYmVkZGluZ19mdW5jdGlvbiJ9CiAgICBfX3B5ZGFudGljX2V4dHJhX18gPSB7ImFsbG93X3BvcHVsYXRpb25fYnlfZmllbGRfbmFtZSI6IFRydWV9CgogICAgY2xhc3MgQ29uZmlnOgogICAgICAgIGFyYml0cmFyeV90eXBlc19hbGxvd2VkID0gVHJ1ZQogICAgICAgIF9fcHlkYW50aWNfZXh0cmFfXyA9IHsiYWxsb3dfcG9wdWxhdGlvbl9ieV9maWVsZF9uYW1lIjogVHJ1ZX0KCiAgICBkZWYgX19pbml0X18oc2VsZikgLT4gTm9uZToKICAgICAgICAiIiIKICAgICAgICBJbml0aWFsaXplcyB0aGUgVGlrVG9rZW5NYW5hZ2VyIG9iamVjdCB3aXRoIHRoZSBwcm92aWRlZCBrZXl3b3JkIGFyZ3VtZW50cy4KCiAgICAgICAgUGFyYW1ldGVyczoKICAgICAgICAgICAgKiprd2FyZ3MgKGRpY3QpOiBBIGRpY3Rpb25hcnkgb2Yga2V5d29yZCBhcmd1bWVudHMuCiAgICAgICAgICAgICAgICAtIHRvdGFsIChpbnQpOiBUaGUgdG90YWwgbnVtYmVyIG9mIHRva2Vucy4KICAgICAgICAgICAgICAgIC0gcmVzcG9uc2VfdG9rZW5zIChpbnQpOiBUaGUgbnVtYmVyIG9mIHJlc3BvbnNlIHRva2Vucy4KICAgICAgICAgICAgICAgIC0gcHJvbXB0X3Rva2VucyAoaW50KTogVGhlIG51bWJlciBvZiBwcm9tcHQgdG9rZW5zLgoKICAgICAgICBSZXR1cm5zOgogICAgICAgICAgICBOb25lCiAgICAgICAgIiIiCiAgICAgICAgc3VwZXIoKS5fX2luaXRfXygpCiAgICAgICAgc2VsZi50b2tlbl91c2FnZTogVG9rZW5Vc2FnZSA9IFRva2VuVXNhZ2UoKQogICAgICAgIHNlbGYuaGlzdG9yaWNhbF9saXN0OiBMaXN0W1Rva2VuVXNhZ2VdID0gW10KICAgICAgICBzZWxmLmVtYmVkZGluZ19mdW5jdGlvbjogRW5jb2RpbmcgPSBlbmNvZGluZygiY2wxMDBrX2Jhc2UiKQoKICAgIGRlZiByZW1vdmUoc2VsZiwgaW5kZXgpIC0+IFRva2VuVXNhZ2U6CiAgICAgICAgIiIiCiAgICAgICAgUmVtb3ZlIGFuIGVsZW1lbnQgZnJvbSB0aGUgaGlzdG9yaWNhbCBsaXN0IGF0IHRoZSBzcGVjaWZpZWQgaW5kZXguCgogICAgICAgIFBhcmFtZXRlcnM6CiAgICAgICAgICAgIGluZGV4IChpbnQpOiBUaGUgaW5kZXggb2YgdGhlIGVsZW1lbnQgdG8gcmVtb3ZlLgoKICAgICAgICBSZXR1cm5zOgogICAgICAgICAgICBzdHI6IEEgbWVzc2FnZSBpbmRpY2F0aW5nIHRoYXQgdGhlIGluZGV4IGhhcyBiZWVuIHJlbW92ZWQuCgogICAgICAgIFJhaXNlczoKICAgICAgICAgICAgSW5kZXhFcnJvcjogSWYgdGhlIGluZGV4IGlzIG91dCBvZiByYW5nZS4KCiAgICAgICAgU2lkZSBFZmZlY3RzOgogICAgICAgICAgICAtIFRoZSBlbGVtZW50IGF0IHRoZSBzcGVjaWZpZWQgaW5kZXggaXMgcmVtb3ZlZCBmcm9tIHRoZSBoaXN0b3JpY2FsIGxpc3QuCiAgICAgICAgICAgIC0gSWYgdGhlIGluZGV4IGlzIDAsIHRoZSBzZXNzaW9uX3RvdGFsLCBwcm9tcHRfdG9rZW5zLCByZXF1ZXN0X3Rva2VucywgcmVzcG9uc2VfdG9rZW5zLCBhbmQgaGlzdG9yaWNhbF9saXN0IGF0dHJpYnV0ZXMgYXJlIHJlc2V0IHRvIDAgb3IgYW4gZW1wdHkgbGlzdC4KICAgICAgICAiIiIKICAgICAgICBzZWxmLmhpc3RvcmljYWxfbGlzdC5yZW1vdmUoc2VsZi5oaXN0b3JpY2FsX2xpc3RbaW5kZXhdKQogICAgICAgIGlmIGluZGV4ID09IDA6CiAgICAgICAgICAgIHNlbGYudG9rZW5fdXNhZ2UudG90YWxfdG9rZW5zID0gMAogICAgICAgICAgICBzZWxmLnRva2VuX3VzYWdlLnByb21wdF90b2tlbnMgPSAwCiAgICAgICAgICAgIHNlbGYudG9rZW5fdXNhZ2UucmVxdWVzdF90b2tlbnMgPSAwCiAgICAgICAgICAgIHNlbGYudG9rZW5fdXNhZ2UucmVzcG9uc2VfdG9rZW5zID0gMAogICAgICAgICAgICBzZWxmLmhpc3RvcmljYWxfbGlzdC5hcHBlbmQoVG9rZW5Vc2FnZSgqKnNlbGYudG9rZW5fdXNhZ2UubW9kZWxfZHVtcCgpKSkKCiAgICAgICAgcmV0dXJuIHNlbGYudG9rZW5fdXNhZ2UKCiAgICBkZWYgdXBkYXRlKHNlbGYsIHJlcXVlc3Q6IGludCwgcmVzcG9uc2U6IGludCkgLT4gVG9rZW5Vc2FnZToKICAgICAgICAiIiIKICAgICAgICBVcGRhdGVzIHRoZSBzZXNzaW9uIHRvdGFsLCBwcm9tcHQgdG9rZW5zLCByZXF1ZXN0IHRva2VucywgYW5kIHJlc3BvbnNlIHRva2VucyB3aXRoIHRoZSBwcm92aWRlZCB2YWx1ZXMuCgogICAgICAgIFBhcmFtZXRlcnM6CiAgICAgICAgICAgIHRvdGFsIChpbnQpOiBUaGUgdG90YWwgbnVtYmVyIG9mIHRva2Vucy4KICAgICAgICAgICAgcmVxdWVzdCAoaW50KTogVGhlIG51bWJlciBvZiByZXF1ZXN0IHRva2Vucy4KICAgICAgICAgICAgcmVzcG9uc2UgKGludCk6IFRoZSBudW1iZXIgb2YgcmVzcG9uc2UgdG9rZW5zLgoKICAgICAgICBSZXR1cm5zOgogICAgICAgICAgICBzdHI6IEEgbWVzc2FnZSBpbmRpY2F0aW5nIHRoYXQgdGhlIHVwZGF0ZSB3YXMgc3VjY2Vzc2Z1bC4KICAgICAgICAiIiIKICAgICAgICBzZWxmLnRva2VuX3VzYWdlLnJlcXVlc3RfdG9rZW5zID0gcmVxdWVzdCBvciAwCiAgICAgICAgc2VsZi50b2tlbl91c2FnZS5yZXNwb25zZV90b2tlbnMgPSByZXNwb25zZSBvciAwCiAgICAgICAgc2VsZi50b2tlbl91c2FnZS5wcm9tcHRfdG9rZW5zID0gc2VsZi50b2tlbl91c2FnZS5yZXF1ZXN0X3Rva2VucyArIHNlbGYudG9rZW5fdXNhZ2UucmVzcG9uc2VfdG9rZW5zCiAgICAgICAgc2VsZi50b2tlbl91c2FnZS50b3RhbF90b2tlbnMgKz0gc2VsZi50b2tlbl91c2FnZS5wcm9tcHRfdG9rZW5zCiAgICAgICAgc2VsZi5oaXN0b3JpY2FsX2xpc3QuYXBwZW5kKFRva2VuVXNhZ2UoKipzZWxmLnRva2VuX3VzYWdlLm1vZGVsX2R1bXAoKSkpCiAgICAgICAgcmV0dXJuIHNlbGYudG9rZW5fdXNhZ2UKCiAgICBkZWYgY291bnRfdG9rZW5zKHNlbGYsIHN0cmluZzogc3RyLCBlbmNvZGluZ19uYW1lOiBzdHIgPSAiY2wxMDBrX2Jhc2UiKSAtPiBpbnQ6CiAgICAgICAgIiIiCiAgICAgICAgQ291bnRzIHRoZSBudW1iZXIgb2YgdG9rZW5zIGluIGEgZ2l2ZW4gc3RyaW5nIHVzaW5nIHRoZSBzcGVjaWZpZWQgZW5jb2RpbmcuCgogICAgICAgIFBhcmFtZXRlcnM6CiAgICAgICAgICAgIHN0cmluZyAoc3RyKTogVGhlIGlucHV0IHN0cmluZyB0byBjb3VudCB0aGUgdG9rZW5zIG9mLgogICAgICAgICAgICBlbmNvZGluZ19uYW1lIChzdHIsIG9wdGlvbmFsKTogVGhlIG5hbWUgb2YgdGhlIGVuY29kaW5nIHRvIHVzZS4gRGVmYXVsdHMgdG8gImNsMTAwa19iYXNlIi4KCiAgICAgICAgUmV0dXJuczoKICAgICAgICAgICAgaW50OiBUaGUgbnVtYmVyIG9mIHRva2VucyBpbiB0aGUgaW5wdXQgc3RyaW5nLgogICAgICAgICIiIgogICAgICAgIGVtYmVkZGluZ19hcnJheTogdGlrdG9rZW4uRW5jb2RpbmcgPSB0aWt0b2tlbi5nZXRfZW5jb2RpbmcoCiAgICAgICAgICAgIGVuY29kaW5nX25hbWU9ZW5jb2RpbmdfbmFtZQogICAgICAgICkKICAgICAgICByZXR1cm4gbGVuKGVtYmVkZGluZ19hcnJheS5lbmNvZGUodGV4dD1zdHJpbmcpKQoKICAgIGRlZiBjb3NpbmVfc2ltaWxhcml0eSgKICAgICAgICBzZWxmLCBlbWJlZGRpbmcxOiBMaXN0W2ludF0sIGVtYmVkZGluZzI6IExpc3RbaW50XQogICAgKSAtPiBmbG9hdGluZ1tfNjRCaXQgfCBBbnldOgogICAgICAgICIiIgogICAgICAgIENhbGN1bGF0ZXMgdGhlIGNvc2luZSBzaW1pbGFyaXR5IGJldHdlZW4gdHdvIGVtYmVkZGluZ3MuCgogICAgICAgIFBhcmFtZXRlcnM6CiAgICAgICAgICAgIGVtYmVkZGluZzEgKExpc3RbaW50XSk6IFRoZSBmaXJzdCBlbWJlZGRpbmcuCiAgICAgICAgICAgIGVtYmVkZGluZzIgKExpc3RbaW50XSk6IFRoZSBzZWNvbmQgZW1iZWRkaW5nLgoKICAgICAgICBSZXR1cm5zOgogICAgICAgICAgICBmbG9hdDogVGhlIGNvc2luZSBzaW1pbGFyaXR5IGJldHdlZW4gdGhlIHR3byBlbWJlZGRpbmdzLgogICAgICAgICIiIgogICAgICAgIGZyb20gc2NpcHkuc3BhdGlhbCBpbXBvcnQgZGlzdGFuY2UKICAgICAgICBpbXBvcnQgbnVtcHkgYXMgbnAKCiAgICAgICAgbnBfZW1iZWRkaW5nMSA9IG5wLmFycmF5KG9iamVjdD1lbWJlZGRpbmcxKQogICAgICAgIG5wX2VtYmVkZGluZzIgPSBucC5hcnJheShvYmplY3Q9ZW1iZWRkaW5nMikKICAgICAgICByZXR1cm4gMSAtIGRpc3RhbmNlLmNvc2luZSh1PW5wX2VtYmVkZGluZzEsIHY9bnBfZW1iZWRkaW5nMikKCiAgICBkZWYgcHJvY2VzcyhzZWxmLCBzdHJpbmc6IHN0cikgLT4gTGlzdFtpbnRdOgogICAgICAgIGVtYmVkZGluZyA9IHNlbGYuZW1iZWRkaW5nX2Z1bmN0aW9uLmVuY29kZSh0ZXh0PXN0cmluZykKICAgICAgICBzZWxmLnVwZGF0ZShyZXF1ZXN0PWxlbihlbWJlZGRpbmcpLCByZXNwb25zZT0wKQogICAgICAgIHJldHVybiBlbWJlZGRpbmcKICAgIAogICAgCmlmIF9fbmFtZV9fID09ICdfX21haW5fXyc6CiAgICBtb2R1bGUgPSBFbWJlZGRpbmdNb2R1bGUoKQogICAgcHJpbnQobW9kdWxlLnByb2Nlc3MoImhlbGxvIHdvcmxkIikp'),
    ('tests/test_embedding_module.py', 'aW1wb3J0IHVuaXR0ZXN0CmZyb20gLi5lbWJlZGRpbmcgaW1wb3J0IEVtYmVkZGluZ01vZHVsZQoKCmNsYXNzIFRlc3RFbWJlZGRpbmdNb2R1bGUodW5pdHRlc3QuVGVzdENhc2UpOgogICAgZGVmIHNldFVwKHNlbGYpOgogICAgICAgIHNlbGYubW9kdWxlID0gRW1iZWRkaW5nTW9kdWxlKCkKCiAgICBkZWYgdGVzdF9wcm9jZXNzKHNlbGYpOgogICAgICAgIHJlc3VsdCA9IHNlbGYubW9kdWxlLnByb2Nlc3MoImhlbGxvIHdvcmxkIikKICAgICAgICBzZWxmLmFzc2VydEVxdWFsKHJlc3VsdCwgWzE1MzM5LCAxOTE3XSkKCiAgICBkZWYgdGVzdF90b2tlbl91c2FnZShzZWxmKToKICAgICAgICAjIEFzc3VtaW5nIHByb2Nlc3MoKSB1cGRhdGVzIHRva2VuX3VzYWdlCiAgICAgICAgc2VsZi5tb2R1bGUucHJvY2VzcygiaGVsbG8gd29ybGQiKQogICAgICAgIHRva2VuX3VzYWdlID0gc2VsZi5tb2R1bGUudG9rZW5fdXNhZ2UubW9kZWxfZHVtcCgpCiAgICAgICAgc2VsZi5hc3NlcnRFcXVhbCh0b2tlbl91c2FnZSwgeyd0b3RhbF90b2tlbnMnOiAyLCAncHJvbXB0X3Rva2Vucyc6IDIsICdyZXF1ZXN0X3Rva2Vucyc6IDIsICdyZXNwb25zZV90b2tlbnMnOiAwfSkKCiAgICBkZWYgdGVzdF9jb3NpbmVfc2ltaWxhcml0eV9kaWZmZXJlbnRfdmVjdG9ycyhzZWxmKToKICAgICAgICByZXN1bHQgPSBzZWxmLm1vZHVsZS5jb3NpbmVfc2ltaWxhcml0eShbMSwgMiwgM10sIFswLjAwMDQsIDAuMDAwNSwgMC4wMDAwMDZdKQogICAgICAgIHNlbGYuYXNzZXJ0QWxtb3N0RXF1YWwocmVzdWx0LCAwLjU5MTgzNTc4MjE2NjkzOTksIHBsYWNlcz03KQoKICAgIGRlZiB0ZXN0X2Nvc2luZV9zaW1pbGFyaXR5X2lkZW50aWNhbF92ZWN0b3JzKHNlbGYpOgogICAgICAgIHJlc3VsdCA9IHNlbGYubW9kdWxlLmNvc2luZV9zaW1pbGFyaXR5KFsxLCAyLCAzXSwgWzEsIDIsIDNdKQogICAgICAgIHNlbGYuYXNzZXJ0RXF1YWwocmVzdWx0LCAxLjApCgppZiBfX25hbWVfXyA9PSAnX19tYWluX18nOgogICAgdW5pdHRlc3QubWFpbigp'),
    ('tests/__init__.py', ''),
]

for relative_path, encoded_content in file_data:
    full_path = os.path.join(folder_path, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as f:
        f.write(base64.b64decode(encoded_content))
    print(f'Created: {full_path}')
command = ['bash', 'modules/embedding/install_embedding.sh']
subprocess.run(command, check=True)