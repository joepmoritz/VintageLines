import os, shutil, math, sublime, sublime_plugin, types

class VintageLinesEventListener(sublime_plugin.EventListener):
	def __init__(self):
		self.in_check_settings = False
		self.icon_count = 99
		self.on_load = self.on_new = self.on_activated

		# Set icon path depending on version
		if int(sublime.version()) >= 3000:
			self.icon_path = "Packages/VintageLines/icons/%s/%s.png"
		else:
			self.icon_path = "../VintageLines/icons/%s/%s"

	def showRelativeNumbers(self):
		view = self.view

		view.settings().set('line_numbers', False)

		current_start = view.rowcol(view.sel()[0].begin())
		current_line_start = current_start[0]
		current_end = view.rowcol(view.sel()[0].end())
		current_line_end = current_end[0]
		start_line = max(current_line_start-self.icon_count, 0)
		end_line = min(current_line_end+self.icon_count, self.view.rowcol(self.view.size())[0])


		line_height = self.view.line_height()
		layout_position_start = self.view.text_to_layout(self.view.text_point(current_start[0], current_start[1]))[1]
		region_number = 1
		for i in range(start_line, current_line_start):
			name = 'linenum' + str(region_number)
			region_number = region_number + 1

			text_point = self.view.text_point(i, 0)
			layout_position = self.view.text_to_layout(text_point)[1]
			icon = str(int(math.fabs((layout_position - layout_position_start) / line_height)))

			line_region = sublime.Region(self.view.text_point(i, 0), self.view.text_point(i, 0))
			view.add_regions(name, [line_region], 'linenums', self.icon_path % (sublime.platform(), icon), sublime.HIDDEN)

		layered_position_end = self.view.text_to_layout(self.view.text_point(current_end[0], current_end[1]))[1]
		for i in range(current_line_end, end_line + 1):
			name = 'linenum' + str(region_number)
			region_number = region_number + 1

			text_point = self.view.text_point(i, 0)
			layout_position = self.view.text_to_layout(text_point)[1]
			icon = str(int(math.fabs((layout_position - layered_position_end) / line_height)))

			line_region = sublime.Region(self.view.text_point(i, 0), self.view.text_point(i, 0))
			view.add_regions(name, [line_region], 'linenums', self.icon_path % (sublime.platform(), icon), sublime.HIDDEN)


	def removeRelativeNumbers(self):
		self.view.settings().set('line_numbers', True)
		# Remove all relative line number regions within viewport
		for i in range(2*self.icon_count+1):
			if self.view.get_regions('linenum' + str(i)):
				self.view.erase_regions('linenum' + str(i))

	def checkSettings(self):
		if not self.view:
			return

		if self.view.settings().has("terminus_view"):
			return

		cur_line = self.view.rowcol(self.view.sel()[0].begin())[0]

		if cur_line == None:
			settings.set("vintage_lines.force_mode", True);

		if self.in_check_settings:
			# As this function is called when a setting changes, and its children also
			# changes settings, we don't want it to end up in an infinite loop.
			return

		self.in_check_settings = True

		if self.view:
			settings = self.view.settings()

			if settings.has("vintage_lines.force_mode"):
				show = settings.get("vintage_lines.force_mode")
			elif type(settings.get('command_mode')) is bool:
				show = settings.get('command_mode')
			else:
				show = False

			mode = settings.get('vintage_lines.mode', False)
			line_start = settings.get('vintage_lines.line_start', -1)
			line_end = settings.get('vintage_lines.line_end', -1)
			lines = settings.get('vintage_lines.lines', -1)

			update = mode != show
			update = update or line_start != self.view.rowcol(self.view.sel()[0].begin())
			update = update or line_end != self.view.rowcol(self.view.sel()[0].end())
			update = update or lines != self.view.rowcol(self.view.size())[0]

			# print("update: %d" % update)
			# print("show: %d" % show)


			if update:
				if show:
					self.removeRelativeNumbers()
					self.showRelativeNumbers()
				else:
					self.removeRelativeNumbers()

				self.view.settings().set('vintage_lines.line_start', self.view.rowcol(self.view.sel()[0].begin()))
				self.view.settings().set('vintage_lines.line_end', self.view.rowcol(self.view.sel()[0].end()))
				self.view.settings().set('vintage_lines.mode', show)
				self.view.settings().set('vintage_lines.lines', self.view.rowcol(self.view.size())[0])

		self.in_check_settings = False

	def on_activated(self, view):
		self.view = view
		if view:
			view.settings().clear_on_change("VintageLines")
			view.settings().set('vintage_lines.line_start', -1) # Just to force an update on activation
			view.settings().set('vintage_lines.line_end', -1) # Just to force an update on activation
			view.settings().add_on_change("VintageLines", self.checkSettings)
		self.checkSettings()

	def on_selection_modified(self, view):
		sublime.set_timeout(self.checkSettings, 10)

