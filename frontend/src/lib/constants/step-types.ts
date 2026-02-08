// Step Types Configuration for Visual Workflow Builder

import type { TriggerType, ActionType } from '@/lib/types/workflow';

export interface StepDefinition {
  type: TriggerType | ActionType;
  category: 'trigger' | 'action' | 'condition' | 'wait' | 'logic';
  label: string;
  description: string;
  icon: string;
  configFields: ConfigField[];
  color: string;
}

export interface ConfigField {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'number' | 'date' | 'time' | 'datetime' | 'toggle' | 'email' | 'phone' | 'multiselect' | 'tags';
  placeholder?: string;
  required: boolean;
  defaultValue?: string | number | boolean | string[];
  options?: { label: string; value: string }[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
  helpText?: string;
  mergeFields?: string[];
}

// Trigger Categories
export const TRIGGER_CATEGORIES = {
  CONTACT: {
    id: 'contact',
    label: 'Contact',
    description: 'Events related to contact records',
    color: 'bg-blue-500',
  },
  FORM: {
    id: 'form',
    label: 'Form',
    description: 'Form submission events',
    color: 'bg-green-500',
  },
  PIPELINE: {
    id: 'pipeline',
    label: 'Pipeline',
    description: 'Pipeline and deal events',
    color: 'bg-purple-500',
  },
  APPOINTMENT: {
    id: 'appointment',
    label: 'Appointment',
    description: 'Calendar and appointment events',
    color: 'bg-orange-500',
  },
  PAYMENT: {
    id: 'payment',
    label: 'Payment',
    description: 'Payment and subscription events',
    color: 'bg-pink-500',
  },
  COMMUNICATION: {
    id: 'communication',
    label: 'Communication',
    description: 'Email, SMS, and call events',
    color: 'bg-cyan-500',
  },
  TIME: {
    id: 'time',
    label: 'Time',
    description: 'Scheduled and recurring events',
    color: 'bg-yellow-500',
  },
  OTHER: {
    id: 'other',
    label: 'Other',
    description: 'Other trigger events',
    color: 'bg-gray-500',
  },
} as const;

// Action Categories
export const ACTION_CATEGORIES = {
  COMMUNICATION: {
    id: 'communication',
    label: 'Communication',
    description: 'Send messages to contacts',
    color: 'bg-blue-500',
  },
  CRM: {
    id: 'crm',
    label: 'CRM',
    description: 'Manage contacts and pipelines',
    color: 'bg-green-500',
  },
  TIMING: {
    id: 'timing',
    label: 'Timing',
    description: 'Add delays and scheduling',
    color: 'bg-purple-500',
  },
  LOGIC: {
    id: 'logic',
    label: 'Logic',
    description: 'Control workflow flow',
    color: 'bg-orange-500',
  },
  INTERNAL: {
    id: 'internal',
    label: 'Internal',
    description: 'Tasks and notifications',
    color: 'bg-pink-500',
  },
  INTEGRATION: {
    id: 'integration',
    label: 'Integration',
    description: 'External webhooks and APIs',
    color: 'bg-cyan-500',
  },
} as const;

// All Trigger Definitions (26 types)
export const TRIGGER_DEFINITIONS: StepDefinition[] = [
  // Contact Triggers
  {
    type: 'contact.created',
    category: 'trigger',
    label: 'Contact Created',
    description: 'When a new contact is created',
    icon: 'UserPlus',
    configFields: [],
    color: TRIGGER_CATEGORIES.CONTACT.color,
  },
  {
    type: 'contact.updated',
    category: 'trigger',
    label: 'Contact Updated',
    description: 'When a contact is updated',
    icon: 'UserEdit',
    configFields: [],
    color: TRIGGER_CATEGORIES.CONTACT.color,
  },
  {
    type: 'contact.tagAdded',
    category: 'trigger',
    label: 'Tag Added',
    description: 'When a tag is added to contact',
    icon: 'Tag',
    configFields: [
      {
        name: 'tagId',
        label: 'Tag',
        type: 'select',
        required: true,
        placeholder: 'Select a tag',
        options: [], // Filled dynamically
        helpText: 'The tag to watch for',
      },
    ],
    color: TRIGGER_CATEGORIES.CONTACT.color,
  },
  {
    type: 'contact.tagRemoved',
    category: 'trigger',
    label: 'Tag Removed',
    description: 'When a tag is removed from contact',
    icon: 'Tag',
    configFields: [
      {
        name: 'tagId',
        label: 'Tag',
        type: 'select',
        required: true,
        placeholder: 'Select a tag',
        options: [],
        helpText: 'The tag to watch for',
      },
    ],
    color: TRIGGER_CATEGORIES.CONTACT.color,
  },
  {
    type: 'contact.birthday',
    category: 'trigger',
    label: 'Contact Birthday',
    description: 'On contact\'s birthday',
    icon: 'Cake',
    configFields: [
      {
        name: 'daysBefore',
        label: 'Days Before Birthday',
        type: 'number',
        required: false,
        defaultValue: 0,
        validation: { min: 0, max: 30 },
        helpText: 'Trigger 0 days = on birthday, 1 day = day before',
      },
    ],
    color: TRIGGER_CATEGORIES.CONTACT.color,
  },
  {
    type: 'contact.anniversary',
    category: 'trigger',
    label: 'Contact Anniversary',
    description: 'On contact anniversary date',
    icon: 'Heart',
    configFields: [
      {
        name: 'customFieldId',
        label: 'Anniversary Field',
        type: 'select',
        required: true,
        placeholder: 'Select custom field',
        options: [],
        helpText: 'Custom field containing anniversary date',
      },
      {
        name: 'daysBefore',
        label: 'Days Before',
        type: 'number',
        required: false,
        defaultValue: 0,
        validation: { min: 0, max: 30 },
      },
    ],
    color: TRIGGER_CATEGORIES.CONTACT.color,
  },

  // Form Triggers
  {
    type: 'form.submitted',
    category: 'trigger',
    label: 'Form Submitted',
    description: 'When a form is submitted',
    icon: 'FileText',
    configFields: [
      {
        name: 'formId',
        label: 'Form',
        type: 'select',
        required: true,
        placeholder: 'Select a form',
        options: [],
        helpText: 'The form to watch',
      },
    ],
    color: TRIGGER_CATEGORIES.FORM.color,
  },

  // Pipeline Triggers
  {
    type: 'pipeline.stageChanged',
    category: 'trigger',
    label: 'Pipeline Stage Changed',
    description: 'When deal moves to a stage',
    icon: 'GitBranch',
    configFields: [
      {
        name: 'pipelineId',
        label: 'Pipeline',
        type: 'select',
        required: true,
        placeholder: 'Select pipeline',
        options: [],
      },
      {
        name: 'stageId',
        label: 'Stage',
        type: 'select',
        required: true,
        placeholder: 'Select stage',
        options: [],
        helpText: 'The stage to trigger on',
      },
    ],
    color: TRIGGER_CATEGORIES.PIPELINE.color,
  },
  {
    type: 'pipeline.stageEntered',
    category: 'trigger',
    label: 'Entered Pipeline Stage',
    description: 'When deal enters a stage',
    icon: 'GitCommit',
    configFields: [
      {
        name: 'pipelineId',
        label: 'Pipeline',
        type: 'select',
        required: true,
        placeholder: 'Select pipeline',
        options: [],
      },
      {
        name: 'stageId',
        label: 'Stage',
        type: 'select',
        required: true,
        placeholder: 'Select stage',
        options: [],
      },
    ],
    color: TRIGGER_CATEGORIES.PIPELINE.color,
  },

  // Appointment Triggers
  {
    type: 'appointment.booked',
    category: 'trigger',
    label: 'Appointment Booked',
    description: 'When appointment is booked',
    icon: 'CalendarPlus',
    configFields: [
      {
        name: 'calendarId',
        label: 'Calendar',
        type: 'select',
        required: false,
        placeholder: 'Select calendar (optional)',
        options: [],
        helpText: 'Leave empty for all calendars',
      },
    ],
    color: TRIGGER_CATEGORIES.APPOINTMENT.color,
  },
  {
    type: 'appointment.cancelled',
    category: 'trigger',
    label: 'Appointment Cancelled',
    description: 'When appointment is cancelled',
    icon: 'CalendarX',
    configFields: [
      {
        name: 'calendarId',
        label: 'Calendar',
        type: 'select',
        required: false,
        placeholder: 'Select calendar (optional)',
        options: [],
      },
    ],
    color: TRIGGER_CATEGORIES.APPOINTMENT.color,
  },
  {
    type: 'appointment.completed',
    category: 'trigger',
    label: 'Appointment Completed',
    description: 'When appointment is completed',
    icon: 'CalendarCheck',
    configFields: [
      {
        name: 'calendarId',
        label: 'Calendar',
        type: 'select',
        required: false,
        placeholder: 'Select calendar (optional)',
        options: [],
      },
    ],
    color: TRIGGER_CATEGORIES.APPOINTMENT.color,
  },
  {
    type: 'appointment.noShow',
    category: 'trigger',
    label: 'Appointment No-Show',
    description: 'When contact misses appointment',
    icon: 'UserX',
    configFields: [
      {
        name: 'calendarId',
        label: 'Calendar',
        type: 'select',
        required: false,
        placeholder: 'Select calendar (optional)',
        options: [],
      },
    ],
    color: TRIGGER_CATEGORIES.APPOINTMENT.color,
  },

  // Payment Triggers
  {
    type: 'payment.received',
    category: 'trigger',
    label: 'Payment Received',
    description: 'When payment is received',
    icon: 'DollarSign',
    configFields: [
      {
        name: 'minAmount',
        label: 'Minimum Amount',
        type: 'number',
        required: false,
        placeholder: '0.00',
        validation: { min: 0 },
        helpText: 'Only trigger for payments above this amount',
      },
    ],
    color: TRIGGER_CATEGORIES.PAYMENT.color,
  },
  {
    type: 'payment.failed',
    category: 'trigger',
    label: 'Payment Failed',
    description: 'When payment fails',
    icon: 'XCircle',
    configFields: [],
    color: TRIGGER_CATEGORIES.PAYMENT.color,
  },
  {
    type: 'subscription.created',
    category: 'trigger',
    label: 'Subscription Created',
    description: 'When subscription is created',
    icon: 'CreditCard',
    configFields: [
      {
        name: 'productId',
        label: 'Product/Plan',
        type: 'select',
        required: false,
        placeholder: 'Select product (optional)',
        options: [],
      },
    ],
    color: TRIGGER_CATEGORIES.PAYMENT.color,
  },
  {
    type: 'subscription.cancelled',
    category: 'trigger',
    label: 'Subscription Cancelled',
    description: 'When subscription is cancelled',
    icon: 'UserMinus',
    configFields: [
      {
        name: 'productId',
        label: 'Product/Plan',
        type: 'select',
        required: false,
        placeholder: 'Select product (optional)',
        options: [],
      },
    ],
    color: TRIGGER_CATEGORIES.PAYMENT.color,
  },

  // Communication Triggers
  {
    type: 'email.opened',
    category: 'trigger',
    label: 'Email Opened',
    description: 'When email is opened',
    icon: 'MailOpen',
    configFields: [],
    color: TRIGGER_CATEGORIES.COMMUNICATION.color,
  },
  {
    type: 'email.clicked',
    category: 'trigger',
    label: 'Email Link Clicked',
    description: 'When link in email is clicked',
    icon: 'MousePointerClick',
    configFields: [],
    color: TRIGGER_CATEGORIES.COMMUNICATION.color,
  },
  {
    type: 'sms.replied',
    category: 'trigger',
    label: 'SMS Replied',
    description: 'When contact replies to SMS',
    icon: 'MessageSquareReply',
    configFields: [],
    color: TRIGGER_CATEGORIES.COMMUNICATION.color,
  },
  {
    type: 'call.completed',
    category: 'trigger',
    label: 'Call Completed',
    description: 'When call is completed',
    icon: 'Phone',
    configFields: [],
    color: TRIGGER_CATEGORIES.COMMUNICATION.color,
  },

  // Time Triggers
  {
    type: 'specific.datetime',
    category: 'trigger',
    label: 'Specific Date/Time',
    description: 'At a specific date and time',
    icon: 'Clock',
    configFields: [
      {
        name: 'datetime',
        label: 'Date & Time',
        type: 'datetime',
        required: true,
        helpText: 'When to trigger the workflow',
      },
    ],
    color: TRIGGER_CATEGORIES.TIME.color,
  },
  {
    type: 'recurring.schedule',
    category: 'trigger',
    label: 'Recurring Schedule',
    description: 'On a recurring schedule',
    icon: 'RefreshCw',
    configFields: [
      {
        name: 'frequency',
        label: 'Frequency',
        type: 'select',
        required: true,
        options: [
          { label: 'Daily', value: 'daily' },
          { label: 'Weekly', value: 'weekly' },
          { label: 'Monthly', value: 'monthly' },
          { label: 'Yearly', value: 'yearly' },
        ],
      },
      {
        name: 'time',
        label: 'Time',
        type: 'time',
        required: true,
      },
      {
        name: 'dayOfWeek',
        label: 'Day of Week',
        type: 'select',
        required: false,
        options: [
          { label: 'Monday', value: '1' },
          { label: 'Tuesday', value: '2' },
          { label: 'Wednesday', value: '3' },
          { label: 'Thursday', value: '4' },
          { label: 'Friday', value: '5' },
          { label: 'Saturday', value: '6' },
          { label: 'Sunday', value: '0' },
        ],
        helpText: 'Required for weekly frequency',
      },
      {
        name: 'dayOfMonth',
        label: 'Day of Month',
        type: 'number',
        required: false,
        validation: { min: 1, max: 31 },
        helpText: 'Required for monthly frequency',
      },
    ],
    color: TRIGGER_CATEGORIES.TIME.color,
  },

  // Goal Triggers
  {
    type: 'goal.completed',
    category: 'trigger',
    label: 'Goal Completed',
    description: 'When a goal is achieved',
    icon: 'Target',
    configFields: [
      {
        name: 'goalId',
        label: 'Goal',
        type: 'select',
        required: true,
        placeholder: 'Select a goal',
        options: [],
      },
    ],
    color: TRIGGER_CATEGORIES.OTHER.color,
  },

  // Webhook Triggers
  {
    type: 'webhook.received',
    category: 'trigger',
    label: 'Webhook Received',
    description: 'When webhook is received',
    icon: 'Webhook',
    configFields: [],
    color: TRIGGER_CATEGORIES.OTHER.color,
  },
];

// All Action Definitions (25+ types)
export const ACTION_DEFINITIONS: StepDefinition[] = [
  // Communication Actions
  {
    type: 'communication.sendEmail',
    category: 'action',
    label: 'Send Email',
    description: 'Send an email to the contact',
    icon: 'Mail',
    configFields: [
      {
        name: 'templateId',
        label: 'Email Template',
        type: 'select',
        required: true,
        placeholder: 'Select template',
        options: [],
        helpText: 'Choose from your email templates',
      },
      {
        name: 'subject',
        label: 'Subject',
        type: 'text',
        required: true,
        placeholder: 'Enter email subject',
        mergeFields: ['contact.firstName', 'contact.lastName', 'contact.email'],
      },
      {
        name: 'body',
        label: 'Email Body',
        type: 'textarea',
        required: true,
        placeholder: 'Enter email content',
        helpText: 'Use {{contact.field}} for merge fields',
        mergeFields: ['contact.*'],
      },
      {
        name: 'fromEmail',
        label: 'From Email',
        type: 'email',
        required: false,
        placeholder: 'sender@example.com',
      },
      {
        name: 'fromName',
        label: 'From Name',
        type: 'text',
        required: false,
        placeholder: 'Sender Name',
      },
    ],
    color: ACTION_CATEGORIES.COMMUNICATION.color,
  },
  {
    type: 'communication.sendSms',
    category: 'action',
    label: 'Send SMS',
    description: 'Send a text message',
    icon: 'MessageSquare',
    configFields: [
      {
        name: 'message',
        label: 'Message',
        type: 'textarea',
        required: true,
        placeholder: 'Enter your message',
        helpText: 'Max 160 characters. Use {{contact.field}} for personalization',
        mergeFields: ['contact.firstName', 'contact.lastName', 'contact.phone'],
        validation: { max: 160 },
      },
    ],
    color: ACTION_CATEGORIES.COMMUNICATION.color,
  },
  {
    type: 'communication.sendVoice',
    category: 'action',
    label: 'Send Voice Broadcast',
    description: 'Send a voice message',
    icon: 'PhoneCall',
    configFields: [
      {
        name: 'recordingId',
        label: 'Voice Recording',
        type: 'select',
        required: true,
        placeholder: 'Select recording',
        options: [],
      },
    ],
    color: ACTION_CATEGORIES.COMMUNICATION.color,
  },
  {
    type: 'communication.sendFacebookMessage',
    category: 'action',
    label: 'Send Facebook Message',
    description: 'Send a Facebook message',
    icon: 'MessageCircle',
    configFields: [
      {
        name: 'message',
        label: 'Message',
        type: 'textarea',
        required: true,
        placeholder: 'Enter your message',
      },
    ],
    color: ACTION_CATEGORIES.COMMUNICATION.color,
  },
  {
    type: 'communication.makeCall',
    category: 'action',
    label: 'Make Phone Call',
    description: 'Trigger a phone call',
    icon: 'PhoneOutgoing',
    configFields: [
      {
        name: 'scriptId',
        label: 'Call Script',
        type: 'select',
        required: false,
        placeholder: 'Select script (optional)',
        options: [],
      },
    ],
    color: ACTION_CATEGORIES.COMMUNICATION.color,
  },

  // CRM Actions
  {
    type: 'crm.addTag',
    category: 'action',
    label: 'Add Tag',
    description: 'Add a tag to the contact',
    icon: 'Tag',
    configFields: [
      {
        name: 'tagId',
        label: 'Tag',
        type: 'select',
        required: true,
        placeholder: 'Select tag',
        options: [],
      },
    ],
    color: ACTION_CATEGORIES.CRM.color,
  },
  {
    type: 'crm.removeTag',
    category: 'action',
    label: 'Remove Tag',
    description: 'Remove a tag from contact',
    icon: 'X',
    configFields: [
      {
        name: 'tagId',
        label: 'Tag',
        type: 'select',
        required: true,
        placeholder: 'Select tag',
        options: [],
      },
    ],
    color: ACTION_CATEGORIES.CRM.color,
  },
  {
    type: 'crm.setCustomField',
    category: 'action',
    label: 'Set Custom Field',
    description: 'Set a custom field value',
    icon: 'Settings',
    configFields: [
      {
        name: 'fieldId',
        label: 'Field',
        type: 'select',
        required: true,
        placeholder: 'Select field',
        options: [],
      },
      {
        name: 'value',
        label: 'Value',
        type: 'text',
        required: true,
        placeholder: 'Enter value',
        mergeFields: ['contact.*'],
      },
    ],
    color: ACTION_CATEGORIES.CRM.color,
  },
  {
    type: 'crm.addToPipeline',
    category: 'action',
    label: 'Add to Pipeline',
    description: 'Create deal in pipeline',
    icon: 'GitMerge',
    configFields: [
      {
        name: 'pipelineId',
        label: 'Pipeline',
        type: 'select',
        required: true,
        placeholder: 'Select pipeline',
        options: [],
      },
      {
        name: 'stageId',
        label: 'Stage',
        type: 'select',
        required: true,
        placeholder: 'Select stage',
        options: [],
      },
      {
        name: 'dealName',
        label: 'Deal Name',
        type: 'text',
        required: true,
        placeholder: 'Deal name',
        mergeFields: ['contact.firstName', 'contact.company'],
      },
      {
        name: 'dealValue',
        label: 'Deal Value',
        type: 'number',
        required: false,
        placeholder: '0.00',
      },
    ],
    color: ACTION_CATEGORIES.CRM.color,
  },
  {
    type: 'crm.changePipelineStage',
    category: 'action',
    label: 'Change Pipeline Stage',
    description: 'Move deal to different stage',
    icon: 'GitBranch',
    configFields: [
      {
        name: 'pipelineId',
        label: 'Pipeline',
        type: 'select',
        required: true,
        placeholder: 'Select pipeline',
        options: [],
      },
      {
        name: 'stageId',
        label: 'New Stage',
        type: 'select',
        required: true,
        placeholder: 'Select stage',
        options: [],
      },
    ],
    color: ACTION_CATEGORIES.CRM.color,
  },
  {
    type: 'crm.assignToUser',
    category: 'action',
    label: 'Assign to User',
    description: 'Assign contact to a user',
    icon: 'UserCheck',
    configFields: [
      {
        name: 'userId',
        label: 'User',
        type: 'select',
        required: true,
        placeholder: 'Select user',
        options: [],
      },
    ],
    color: ACTION_CATEGORIES.CRM.color,
  },

  // Timing Actions
  {
    type: 'timing.wait',
    category: 'wait',
    label: 'Wait',
    description: 'Add a delay',
    icon: 'Clock',
    configFields: [
      {
        name: 'duration',
        label: 'Duration',
        type: 'number',
        required: true,
        defaultValue: 1,
        validation: { min: 1 },
      },
      {
        name: 'unit',
        label: 'Unit',
        type: 'select',
        required: true,
        defaultValue: 'hours',
        options: [
          { label: 'Minutes', value: 'minutes' },
          { label: 'Hours', value: 'hours' },
          { label: 'Days', value: 'days' },
          { label: 'Weeks', value: 'weeks' },
        ],
      },
    ],
    color: ACTION_CATEGORIES.TIMING.color,
  },
  {
    type: 'timing.waitUntil',
    category: 'wait',
    label: 'Wait Until',
    description: 'Wait until specific date/time',
    icon: 'CalendarClock',
    configFields: [
      {
        name: 'datetime',
        label: 'Date & Time',
        type: 'datetime',
        required: true,
        helpText: 'Wait until this date and time',
      },
    ],
    color: ACTION_CATEGORIES.TIMING.color,
  },
  {
    type: 'timing.schedule',
    category: 'wait',
    label: 'Schedule',
    description: 'Schedule for later',
    icon: 'Calendar',
    configFields: [
      {
        name: 'datetime',
        label: 'Date & Time',
        type: 'datetime',
        required: true,
      },
    ],
    color: ACTION_CATEGORIES.TIMING.color,
  },

  // Logic Actions
  {
    type: 'logic.ifElse',
    category: 'condition',
    label: 'If/Else',
    description: 'Branch based on conditions',
    icon: 'GitBranch',
    configFields: [
      {
        name: 'conditions',
        label: 'Conditions',
        type: 'multiselect',
        required: true,
        placeholder: 'Select conditions',
        helpText: 'Define branching logic',
      },
      {
        name: 'operator',
        label: 'Logic Operator',
        type: 'select',
        required: true,
        defaultValue: 'AND',
        options: [
          { label: 'All (AND)', value: 'AND' },
          { label: 'Any (OR)', value: 'OR' },
        ],
      },
    ],
    color: ACTION_CATEGORIES.LOGIC.color,
  },
  {
    type: 'logic.splitTest',
    category: 'logic',
    label: 'Split Test',
    description: 'A/B test with paths',
    icon: 'GitCompare',
    configFields: [
      {
        name: 'paths',
        label: 'Number of Paths',
        type: 'number',
        required: true,
        defaultValue: 2,
        validation: { min: 2, max: 5 },
      },
      {
        name: 'distribution',
        label: 'Distribution',
        type: 'select',
        required: true,
        defaultValue: 'equal',
        options: [
          { label: 'Equal', value: 'equal' },
          { label: 'Custom', value: 'custom' },
        ],
      },
    ],
    color: ACTION_CATEGORIES.LOGIC.color,
  },
  {
    type: 'logic.goal',
    category: 'logic',
    label: 'Goal',
    description: 'Track goal achievement',
    icon: 'Target',
    configFields: [
      {
        name: 'goalName',
        label: 'Goal Name',
        type: 'text',
        required: true,
        placeholder: 'My Goal',
      },
      {
        name: 'timeout',
        label: 'Timeout (minutes)',
        type: 'number',
        required: false,
        placeholder: '1440',
        validation: { min: 1 },
        helpText: 'Default: 1440 (24 hours)',
      },
    ],
    color: ACTION_CATEGORIES.LOGIC.color,
  },

  // Internal Actions
  {
    type: 'internal.createTask',
    category: 'action',
    label: 'Create Task',
    description: 'Create a task for users',
    icon: 'CheckSquare',
    configFields: [
      {
        name: 'title',
        label: 'Task Title',
        type: 'text',
        required: true,
        placeholder: 'Enter task title',
      },
      {
        name: 'description',
        label: 'Description',
        type: 'textarea',
        required: false,
        placeholder: 'Task details',
      },
      {
        name: 'assigneeId',
        label: 'Assign To',
        type: 'select',
        required: false,
        placeholder: 'Select user',
        options: [],
      },
      {
        name: 'dueDate',
        label: 'Due Date',
        type: 'date',
        required: false,
      },
      {
        name: 'priority',
        label: 'Priority',
        type: 'select',
        required: false,
        defaultValue: 'medium',
        options: [
          { label: 'Low', value: 'low' },
          { label: 'Medium', value: 'medium' },
          { label: 'High', value: 'high' },
        ],
      },
    ],
    color: ACTION_CATEGORIES.INTERNAL.color,
  },
  {
    type: 'internal.sendNotification',
    category: 'action',
    label: 'Send Notification',
    description: 'Send notification to users',
    icon: 'Bell',
    configFields: [
      {
        name: 'message',
        label: 'Message',
        type: 'textarea',
        required: true,
        placeholder: 'Notification message',
      },
      {
        name: 'recipientIds',
        label: 'Recipients',
        type: 'multiselect',
        required: true,
        placeholder: 'Select users',
        options: [],
      },
    ],
    color: ACTION_CATEGORIES.INTERNAL.color,
  },

  // Integration Actions
  {
    type: 'webhook.call',
    category: 'action',
    label: 'Webhook',
    description: 'Call external webhook',
    icon: 'Webhook',
    configFields: [
      {
        name: 'url',
        label: 'Webhook URL',
        type: 'text',
        required: true,
        placeholder: 'https://api.example.com/webhook',
        validation: { pattern: '^https?://' },
      },
      {
        name: 'method',
        label: 'HTTP Method',
        type: 'select',
        required: true,
        defaultValue: 'POST',
        options: [
          { label: 'POST', value: 'POST' },
          { label: 'GET', value: 'GET' },
          { label: 'PUT', value: 'PUT' },
          { label: 'DELETE', value: 'DELETE' },
        ],
      },
      {
        name: 'headers',
        label: 'Headers (JSON)',
        type: 'textarea',
        required: false,
        placeholder: '{"Authorization": "Bearer token"}',
        helpText: 'JSON format headers',
      },
      {
        name: 'body',
        label: 'Body (JSON)',
        type: 'textarea',
        required: false,
        placeholder: '{"key": "value"}',
        helpText: 'JSON request body',
        mergeFields: ['contact.*'],
      },
      {
        name: 'retryOnFailure',
        label: 'Retry on Failure',
        type: 'toggle',
        required: false,
        defaultValue: true,
      },
      {
        name: 'maxRetries',
        label: 'Max Retries',
        type: 'number',
        required: false,
        defaultValue: 3,
        validation: { min: 0, max: 10 },
      },
    ],
    color: ACTION_CATEGORIES.INTEGRATION.color,
  },
];

// Helper functions
export function getTriggerDefinition(type: TriggerType): StepDefinition | undefined {
  return TRIGGER_DEFINITIONS.find((t) => t.type === type);
}

export function getActionDefinition(type: ActionType): StepDefinition | undefined {
  return ACTION_DEFINITIONS.find((a) => a.type === type);
}

export function getAllStepsByCategory(category: string): StepDefinition[] {
  const triggerCat = (TRIGGER_CATEGORIES as Record<string, { id: string } | undefined>)[category.toUpperCase()];
  const actionCat = (ACTION_CATEGORIES as Record<string, { id: string } | undefined>)[category.toUpperCase()];
  return [
    ...TRIGGER_DEFINITIONS.filter((t) => triggerCat?.id === category),
    ...ACTION_DEFINITIONS.filter((a) => actionCat?.id === category),
  ];
}
