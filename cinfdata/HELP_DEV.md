This file describes different topics relevant to development of the Cinfdata app.

Description of execution flow of different actions
==================================================

Selecting plot
--------------

The following components are involved:
 * `main.py`
  * `Pageselection (class)`
  * `MainCarousel (class)`
  * `DatePlotOptions (class)`
 * `cinfdata.py`
  * `Cinfdata (class)`

Upon clicking one of the buttons that select a plot, the following happens:


 * `PageSelection._select_page method` is called with the **setup** and
   **link** dicts as arguments
 * That method sets the `Cinfdata.selected_plot ObjectProperty[1]`
 * That triggers calling `Cinfdata.on_selected_plot method` which:
 * Resets `Cinfdata.query_args prop` and updates it with information
   from **link['query_args']** (log scale status, min and max,
   plotlists)
 * Then calls `MainCarousel.change_plot method` which, depending on
   the type of the plot, loads the correct settings page (currently
   only `DatePlotOptions`) and sets the `DatePlotOptions.cinfdata
   ObjectProperty`
 * The `DatePlotOptions.__init__ method` only set a few local
   variables
 * The `DatePlotOptions.on_cinfdata method` which is fired
   automcatically when setting the cinfdata ObjectProperty then:
   * Programatically sets up the rest of the gui
   * Set the gui status to reflect **link['query_args']** from the
     query_args
   * Updates the Cinfdata.qeury_args state to reflect it

[1] ObjectProperty is one of kivy's monitored properties
